import machine
import time

from radiacode import RadiaCode
from radiacode.transports.bluetooth import DeviceNotFound as DeviceNotFoundBT
from radiacode import DoseRateDB

BLUETOOTH_MAC = "52:43:06:60:17:dd"
SPECTRUM_DURATION_MS = (60 * 1000)

print(f'Connecting to Radiacode via Bluetooth (MAC address: {BLUETOOTH_MAC})')

while True: 
  try: 
    rc = RadiaCode(bluetooth_mac=BLUETOOTH_MAC)
  except DeviceNotFoundBT as e:
    print(e)
    continue 

  try: 
    serial = rc.serial_number()
    print(f'### Serial number: {serial}')
    print('--------')

    fw_version = rc.fw_version()
    print(f'### Firmware: {fw_version}')
    print('--------')

    spectrum = rc.spectrum()
    print(f'### Spectrum: {spectrum}')
    print('--------')

    # print('### DataBuf:')
    # while True:
    #     for v in rc.data_buf():
    #         print(v.dt.isoformat(), v)

    #     time.sleep(2)
    start = time.ticks_ms() 
    while True: 
      for v in rc.data_buf(): 
        print(v.dt.isoformat(), end=" ")
        if type(v) == DoseRateDB:
          print(v.count, v.count_rate, v.dose_rate, v.dose_rate_err, v.flags)
        else: 
          print(v)
      if time.ticks_ms() - start > SPECTRUM_DURATION_MS:
        start = time.ticks_ms()
        # read the spectrogram 
        spectrum = rc.spectrum()
        print("Spectrum: ", spectrum.counts)
        # restart it 
        rc.spectrum_reset()
        
  except Exception: 
    continue 