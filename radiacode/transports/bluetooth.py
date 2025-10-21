import struct
import platform
import time

class DeviceNotFound(Exception):
    pass

class ConnectionClosed(Exception):
    pass

import bluetooth

from radiacode.bytes_buffer import BytesBuffer

class Bluetooth: 

    def __init__(self, mac, poll_interval: float = 0.01):
        # constructor variables
        self.mac = mac
        self.poll_interval = poll_interval

        # shared variables from original class
        self._resp_buffer = b''
        self._resp_size = 0
        self._response = None
        self._closing = False
        self._connection_state = None

        # new shared variables
        self.ble: bluetooth.BLE = bluetooth.BLE()
        # set up callbacks (notifications)
        self.ble.irq(self.handleNotifications) # link callback 

        # connect to the peripheral 
        self.ble.active(True) # needed before other BLE functions
        # self.ble.config(mac=mac, addr_mode=0x00) # 0x00 == PUBLIC 
        while self._connection_state == None:
            self.ble.gap_connect(
                addr_type=0x00, # PUBLIC
                addr=mac
            )
            # wait for response and try again if disconnect response 
            while self._connection_state == None: 
                time.sleep_ms(10)
            if self._connection_state == _IRQ_PERIPHERAL_DISCONNECT:
                self._connection_state = None
        # we should now be connected 
        assert self._connection_state == _IRQ_PERIPHERAL_CONNECT

        # get the service by UUID 
        
        # get the write_fd characteristics 
        # get the notify_fd characteristics 
        # write to the notify_fd characteristic 


    def handleNotification(self, chandle, data): 
        if chandle == _IRQ_PERIPHERAL_DISCONNECT or chandle == _IRQ_PERIPHERAL_CONNECT:
            self._connection_state = chandle 

        # original library doesn't really use chandle
        # check if this is a new message
            # set up size 
        # copy data into response buffer 
        # reduce size
        # assert < not really needed but helpful 
        # if we've received all of the message (size == 0)
            # copy it over to _response 
            # reset _resp_buffer

        pass

    # synchronized, blocking send msg / receive response 
    def execute(self, req) -> BytesBuffer: 
        # check for closing to be safe 
            # raise error if so 

        # send request
        # loop over request in 18 byte steps 
            # write characteristic to write_fd 

        # wait for response or timeout 
            # waitForNotifications

        # copy response to a new buffer and clear response 
        return BytesBuffer()
    
    def close(self):
        self._closing = True

        time.sleep_ms(100) # 0.1 s 

        # disconnect 

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
