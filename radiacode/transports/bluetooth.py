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

class Bluetooth: 

    def __init__(self, mac, poll_interval: float = 0.01):
        # constructor variables
        self.mac = mac
        self._poll_interval = poll_interval

        # constants
        self._service_UUID = bluetooth.UUID('e63215e5-7003-49d8-96b0-b024798fb901')
        self._write_fd_UUID = bluetooth.UUID('e63215e6-7003-49d8-96b0-b024798fb901')
        self._notify_fd_UUID = bluetooth.UUID('e63215e7-7003-49d8-96b0-b024798fb901')

        # shared variables from original class
        self._resp_buffer = b''
        self._resp_size = 0
        self._response = None
        self._closing = False
        self._connection_state = None

        PUBLIC = 0
        # new shared variables
        self.device = aioble.Device(PUBLIC, self.mac) 

        asyncio.run(self.initialize_async())

    async def initialize_async(self):
        # connect to the peripheral 
        while True:
            try:
                self.connection = await self.device.connect(timeout_ms=2000)
                
                break
            except asyncio.TimeoutError:
                print("Connection failed with Timeout")
        print("Connection:", self.connection)

        # set up callbacks (notifications)
        
        # get the service by UUID - this is automatic client side?
        # self.service = asyncio.run(self.connection.service(self._service_UUID))
        self.service = None 
        
        while self.service == None:
            services = await self._get_services()
            print(services)
            for s in services: 
                if s.uuid == self._service_UUID: 
                    self.service = s
                    break
            if self.service == None:
                print("Failed to find service, retrying...")
        print("Service:", self.service)

        # get characteristics 
        characteristics = await self._get_characteristics()
        print("Characteristics:", characteristics)

        # get the write_fd characteristics 
        self.write_fd = characteristics[self._write_fd_UUID]
        print("Write_fd", self.write_fd)

        # get the notify_fd characteristics 
        self.notify_fd = characteristics[self._write_fd_UUID]
        print("Notify_fd", self.notify_fd)

        # print("Notify_fd descriptors:", self._get_descriptors(self.notify_fd))

        # write to the notify_fd characteristic (subscribe b'\x01\x00')
        # await self.notify_fd.write(b'\x01\x00')
        print("Props:", self.notify_fd.properties)
        await self.notify_fd.subscribe(notify=True)
        # asyncio.run(self.notify_fd.subscribe(notify=True))
        print("Descriptors:", await self._get_descriptors(self.notify_fd))

    async def _get_descriptors(self, target_char):
        descriptors = []
        async for d in target_char.descriptors(): 
            descriptors.append(d)
        return descriptors

    async def _get_characteristics(self):
        characteristics = {}
        async for c in self.service.characteristics():
            characteristics[c.uuid] = c
        return characteristics

    async def _get_services(self):
        result = []
        async for s in self.connection.services():
            result.append(s)
        return result

    def handleNotification(self, data): 
        # check if this is a new message
        if self._resp_size == 0:
            # set up size 
            self._resp_size = 4 + struct.unpack('<i', data[:4])[0]
            self._resp_buffer = data[4:]
        # copy data into response buffer 
        else: 
            self._resp_buffer += data
        # reduce size
        self._resp_size -= len(data)
        # assert not really needed but helpful 
        assert self._resp_size >= 0
        # if we've received all of the message (size == 0)
        if self._resp_size == 0:
            # copy it over to _response 
            self._response = self._resp_buffer
            # reset _resp_buffer
            self._resp_buffer = b''

    # synchronized, blocking send msg / receive response 
    def execute(self, req) -> BytesBuffer:
        return asyncio.run(self.execute_async(req))

    async def execute_async(self, req) -> BytesBuffer: 
        # check for closing to be safe 
        if self._closing: 
            # raise error if so 
            raise ConnectionClosed('Connection is closing')

        # send request
        # loop over request in 18 byte steps 
        for pos in range(0, len(req), 18):
            # write characteristic to write_fd 
            rp = req[pos : min(pos + 18, len(req))]
            await self.write_fd.write(rp)

        # wait for response or timeout 
        timeout_end = time.ticks_ms() + (10 * 1000) # 10 s total timeout 
        while self._response is None and not self._closing: 
            remaining_time = timeout_end - time.ticks_ms()
            if remaining_time <= 0: 
                raise TimeoutError('Response timeout')
            
            poll_time = min(self._poll_interval, remaining_time)
            
            # waitForNotifications
            try: 
                data = asyncio.wait_for(self.notify_fd.notified(), timeout=poll_time)
                self.handleNotification(data)
            except aioble.DeviceDisconnectedError as err:
                raise ConnectionClosed('Bluetooth connection lost') from err
            except asyncio.TimeoutError:
                continue
        if self._closing:
            raise ConnectionClosed('Connection closed while waiting for response')

        # copy response to a new buffer and clear response 
        br = BytesBuffer(self._response)
        self._response = None
        return br 

    def close(self):
        self._closing = True

        time.sleep_ms(100) # 0.1 s 

        # disconnect 
        try: 
            asyncio.run(self.connection.disconnect())
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
