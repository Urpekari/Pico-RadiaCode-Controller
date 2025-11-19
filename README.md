# Pico-RadiaCode-Controller
A controller to handle automated [RadiaCode](https://www.radiacode.com) 10X operation

Based on the [radiacode library](https://github.com/cdump/radiacode) from [cdump](https://github.com/cdump)

### Toolchain
* MicroPython
  * [RPI_PICO_W v1.25.1 (2025-09-11)](https://micropython.org/download/RPI_PICO_W/)
  * [RPI_PICO2_W v1.26.1 (2025-09-11)](https://micropython.org/download/RPI_PICO2_W/)
* [mpremote 1.26.1](https://pypi.org/project/mpremote/) installed with `uv tool install mpremote`
  * [docs](https://docs.micropython.org/en/latest/reference/mpremote.html) 

### Bluetooth MAC
To use the Bluetooth connectivity of the RadiaCode the Pico must know the RadiaCode's Bluetooth MAC Address (defined as a constant in [main.py](/main.py)). 

For example from: 
```
RadiaCode-102#RC-102-006109 52:43:06:60:17:dd
```
Use: 
```python
BLUETOOTH_MAC = "52:43:06:60:17:dd"
```