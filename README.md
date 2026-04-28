# Pico-RadiaCode-Controller
A controller to handle automated [RadiaCode](https://www.radiacode.com) 10X operation

Based on the [radiacode library](https://github.com/cdump/radiacode) from [cdump](https://github.com/cdump)

## Additional compatibility 
This project aims to broaden the scope of the [Original Project](https://github.com/ASU-ASCEND/Pico-RadiaCode-Controller)

It has been tested on the following hardware:
* RP2040 (Raspberry Pi Pico W)
* ESP32-S3 (N16R8)

### Toolchain
* Thonny
* Micropython 1.28 works, older variants will probably work too. (*The original project recommended 1.26*)
* mpremote
* esptool (For ESP32 devices only)

## Deployment notes 
Thankfully micropython is pretty straightforward, but still, just in case.

```
The version here has disabled all SD card functions because we don't have an SD card module ready for our test boards.
We will fix that soon and put the SD card functions back.
```

### RP2040
Copy the following files to the device:
```
	|_ /DataProcessing
	|   |_ process_data.py
	|
	|_ /lib
	|   |_ dataclasses.py
	|   |_ enum.py
	|   |_ sdcard.py
	|
	|_ /radiacode
	|   |_ /decoders
	|   |   |_ databuf.py
	|   |   |_ spectrum.py
	|   |   |_ __init__.py
	|   |
	|   |_ /transports
	|   |   |_ bluetooth.py
	|   |   |_ usb.py
	|   |   |_ __init__.py
	|   |
	|   |_ bytes_buffer.py
	|   |_ radiacode.py
	|   |_ types.py
	|   |_ __init__.py
	|
	|_ boot.py
	|_ datetime.py
	|_ main.py
	|_ process_data.py
```

### ESP32-S3
---
Some ESP32 family of modules (like the ESP32-S3 and ESP32-S2) require a new stub upload config file (in json format) for esptool.

Those files can be found [here](https://github.com/espressif/esptool/tree/master/esptool/targets/stub_flasher)
---
Remove the following lines in main.py:

* Everything between lines 25-31
* Every call to heartbeat()

Copy the following files to the device:

```
	|_ /aioble
	|   |_ central.py
	|   |_ client.py
	|   |_ core.py
	|   |_ device.py
	|   |_ l2cap.py
	|   |_ peripheral.py
	|   |_ security.py
	|   |_ server.py
	|   |_ __init__.py
	|
	|_ /DataProcessing
	|   |_ process_data.py
	|
	|_ /lib
	|   |_ dataclasses.py
	|   |_ enum.py
	|   |_ sdcard.py
	|
	|_ /radiacode
	|   |_ /decoders
	|   |   |_ databuf.py
	|   |   |_ spectrum.py
	|   |   |_ __init__.py
	|   |
	|   |_ /transports
	|   |   |_ bluetooth.py
	|   |   |_ usb.py
	|   |   |_ __init__.py
	|   |
	|   |_ bytes_buffer.py
	|   |_ radiacode.py
	|   |_ types.py
	|   |_ __init__.py
	|
	|_ boot.py
	|_ datetime.py
	|_ main.py
	|_ process_data.py
```

### M5Stack tested pinout
**GNSS (And extra sensors)**:

| Pin Name | GPIO | Used by       |
| -------- | ---- | ------------- |
| PPS      | 10   | GNSS UART     |
| TX       | 18   | GNSS UART     |
| RX       | 17   | GNSS UART     |
| SDA      | 12   | Extra Sensors |
| SCL      | 11   | Extra Sensors |

**LoRa (SX1278)**

| Pin Name | GPIO | 
| ---- | --- | 
| RST  | 5   | 
| CS   | 1   | 
| IRQ  | 14  | 
| MOSI | 37  | 
| MISO | 35  | 
| CLK  | 36  | 

## Bluetooth MAC
To use the Bluetooth connectivity of the RadiaCode the Pico must know the RadiaCode's Bluetooth MAC Address (defined as a constant in [main.py](/main.py)). 

For example from: 
```
RadiaCode-102#RC-102-006109 52:43:06:60:17:dd
```
Use: 
```python
BLUETOOTH_MAC = "52:43:06:60:17:dd"
```

### USB
Working on it...
