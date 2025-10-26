import struct
import platform
import time


class DeviceNotFound(Exception):
    pass


class ConnectionClosed(Exception):
    pass


class TimeoutError(Exception):
    pass


import aioble
import asyncio
import bluetooth

from radiacode.bytes_buffer import BytesBuffer

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)


class Bluetooth:
    def __init__(self, mac, poll_interval: float = 0.01):
        # constructor variables
        self.mac = mac
        self._poll_interval = poll_interval

        # constants
        self._service_UUID = bluetooth.UUID("e63215e5-7003-49d8-96b0-b024798fb901")
        self._write_fd_UUID = bluetooth.UUID("e63215e6-7003-49d8-96b0-b024798fb901")
        self._notify_fd_UUID = bluetooth.UUID("e63215e7-7003-49d8-96b0-b024798fb901")

        # shared variables from original class
        self._resp_buffer = b""
        self._resp_size = 0
        self._response = None
        self._closing = False
        self._connection_state = None

        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        # set up callbacks (notifications)
        self._ble.irq(self.handleNotification)

        # connect to the peripheral
        self.mac_bytes = bytes.fromhex(self.mac.replace(":", ""))
        self._addr_type = 0x00
        self._addr = self.mac_bytes

        self._conn_handle = None
        while self._conn_handle is None:
            self._ble.gap_connect(self._addr_type, self._addr)
            start_time = time.ticks_ms()
            while time.ticks_ms() - start_time < 2000:
                if self._conn_handle is not None:
                    break
                time.sleep_ms(100)
        print("Connection:", self._conn_handle)

        # get the service by UUID
        # get characteristics
        # discover services and UUID
        # get the write_fd characteristics
        # get the notify_fd characteristics
        self._write_fd_handle = None
        self._notify_fd_handle = None
        while (self._write_fd_handle is None) or (self._notify_fd_handle is None):
            # search for any characteristics (this chains)
            self._ble.gattc_discover_services(self._conn_handle, self._service_UUID)
            start_time = time.ticks_ms()
            while time.ticks_ms() - start_time < 2000:
                if (self._write_fd_handle is not None) and (
                    self._notify_fd_handle is not None
                ):
                    break
                time.sleep_ms(100)
            if (self._write_fd_handle is None) or (self._notify_fd_handle is None):
                print("Finding services failed, trying again...")

        # write to the notify_fd characteristic (subscribe b'\x01\x00')
        print("Subscribing")
        # self.p.writeCharacteristic(notify_fd + 1, b'\x01\x00')
        self._notify_fd_cccd_handle = self._notify_fd_handle + 1
        self.blocking_write(self._notify_fd_cccd_handle, b"\x01\x00")

    def blocking_write(self, target_handle, data):
        self._writing = True
        self._ble.gattc_write(self._conn_handle, target_handle, data, 1)
        while self._writing:
            time.sleep_ms(100)

    def handleNotification(self, chandle, data):
        event = chandle
        # print(f"Event! ({event})")
        if event == _IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print("service", data)
            if conn_handle == self._conn_handle and uuid == self._service_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == self._write_fd_UUID:
                self._write_fd_handle = value_handle
            if conn_handle == self._conn_handle and uuid == self._notify_fd_UUID:
                self._notify_fd_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Characteristic query complete.
            if self._notify_fd_handle is not None and self._write_fd_handle is not None:
                pass
            else:
                print("Failed to find characteristics.")

        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            self._writing = False
            # print("Write done.")

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data_mv = data

            notify_data = bytes(notify_data_mv)

            # print(notify_data)

            if value_handle == self._notify_fd_handle:
                # print("notify handle")
                pass

            if value_handle == self._write_fd_handle:
                # print("write handle")
                pass

            # check if this is a new message
            if self._resp_size == 0:
                # set up size
                self._resp_size = 4 + struct.unpack("<i", notify_data[:4])[0]
                self._resp_buffer = notify_data[4:]
            # copy data into response buffer
            else:
                self._resp_buffer += notify_data
            # reduce size
            self._resp_size -= len(notify_data)
            # assert not really needed but helpful
            assert self._resp_size >= 0
            # if we've received all of the message (size == 0)
            if self._resp_size == 0:
                # copy it over to _response
                self._response = self._resp_buffer
                # reset _resp_buffer
                self._resp_buffer = b""

    # synchronized, blocking send msg / receive response
    def execute(self, req) -> BytesBuffer:
        # check for closing to be safe
        if self._closing:
            # raise error if so
            raise ConnectionClosed("Connection is closing")

        # send request
        # loop over request in 18 byte steps
        for pos in range(0, len(req), 18):
            # write characteristic to write_fd
            rp = req[pos : min(pos + 18, len(req))]
            # await self.write_fd.write(rp)
            self.blocking_write(self._write_fd_handle, rp)
            # self._ble.gattc_write(self._conn_handle, self._write_fd_handle, rp)

        # wait for response or timeout
        timeout_end = time.ticks_ms() + (10 * 1000)  # 10 s total timeout
        while self._response is None and not self._closing:
            remaining_time = timeout_end - time.ticks_ms()
            if remaining_time <= 0:
                raise TimeoutError("Response timeout")

            poll_time = min(self._poll_interval, remaining_time)

            # waitForNotifications
            # try:
            #     pass
            #     # data = asyncio.wait_for(self.notify_fd.notified(), timeout=poll_time)
            # except aioble.DeviceDisconnectedError as err:
            #     raise ConnectionClosed('Bluetooth connection lost') from err
            # except asyncio.TimeoutError:
            #     continue
        if self._closing:
            raise ConnectionClosed("Connection closed while waiting for response")

        # copy response to a new buffer and clear response
        br = BytesBuffer(self._response)
        self._response = None
        return br

    def close(self):
        self._closing = True

        time.sleep_ms(100)  # 0.1 s

        # disconnect
        try:
            self._ble.gap_disconnect(self._conn_handle)
        except:
            pass

        self.connection = None


# class Bluetooth(DefaultDelegate):
#     def __init__(self, mac, poll_interval: float = 0.01):
#         """
#         Initialize Bluetooth connection.

#         Args:
#             mac: Bluetooth MAC address
#             poll_interval: How often to poll for notifications (default 0.01s = 10ms)
#                             Shorter intervals provide better shutdown responsiveness.
#         """
#         self._resp_buffer = b''
#         self._resp_size = 0
#         self._response = None
#         self._closing = False
#         self._poll_interval = poll_interval

#         try:
#             self.p = Peripheral(mac)
#         except BTLEDisconnectError as ex:
#             raise DeviceNotFound('Device not found or bluetooth adapter is not powered on') from ex

#         self.p.withDelegate(self)

#         service = self.p.getServiceByUUID('e63215e5-7003-49d8-96b0-b024798fb901')
#         self.write_fd = service.getCharacteristics('e63215e6-7003-49d8-96b0-b024798fb901')[0].getHandle()
#         notify_fd = service.getCharacteristics('e63215e7-7003-49d8-96b0-b024798fb901')[0].getHandle()
#         self.p.writeCharacteristic(notify_fd + 1, b'\x01\x00')

#     def handleNotification(self, chandle, data):
#         if self._resp_size == 0:
#             self._resp_size = 4 + struct.unpack('<i', data[:4])[0]
#             self._resp_buffer = data[4:]
#         else:
#             self._resp_buffer += data
#         self._resp_size -= len(data)
#         assert self._resp_size >= 0
#         if self._resp_size == 0:
#             self._response = self._resp_buffer
#             self._resp_buffer = b''

#     def execute(self, req) -> BytesBuffer:
#         if self._closing:
#             raise ConnectionClosed('Connection is closing')

#         # Send request
#         for pos in range(0, len(req), 18):
#             rp = req[pos : min(pos + 18, len(req))]
#             self.p.writeCharacteristic(self.write_fd, rp)

#         # Poll for response with short intervals for better shutdown responsiveness
#         timeout_end = time.time() + 10.0  # 10 second total timeout
#         while self._response is None and not self._closing:
#             remaining_time = timeout_end - time.time()
#             if remaining_time <= 0:
#                 raise TimeoutError('Response timeout')

#             # Use short poll interval, but not longer than remaining time
#             poll_time = min(self._poll_interval, remaining_time)

#             try:
#                 self.p.waitForNotifications(poll_time)
#             except BTLEDisconnectError as err:
#                 raise ConnectionClosed('Bluetooth connection lost') from err

#         if self._closing:
#             raise ConnectionClosed('Connection closed while waiting for response')

#         br = BytesBuffer(self._response)
#         self._response = None
#         return br

#     def close(self):
#         """Disconnect from the Bluetooth device and release resources."""
#         self._closing = True

#         # Give a brief moment for any pending operations
#         time.sleep(0.1)

#         if hasattr(self, 'p') and self.p is not None:
#             try:
#                 self.p.disconnect()
#             except:  # noqa: E722
#                 pass  # Ignore errors during disconnect
#             self.p = None
