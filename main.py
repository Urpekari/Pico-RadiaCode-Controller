import machine
import time
import os

import sdcard

from radiacode import RadiaCode
from radiacode.transports.bluetooth import DeviceNotFound as DeviceNotFoundBT
from radiacode import DoseRateDB, RareData, RawData, RealTimeData, Event

BLUETOOTH_MAC = "52:43:06:60:17:dd"
SPECTRUM_DURATION_MS = (60 * 1000)

while True: 
  print("Setting up SD card...")
  spi = machine.SPI()
  spi.init()
  sd = sdcard.SDCard(spi, machine.Pin.board.GP17)
  print("Mounting filesystem...")
  vfs = os.VfsFat(sd)
  os.mount(vfs, "/fs")

  it = 0
  data_file_path = "" 
  while True: 
    try: 
      data_file_path = f"/fs/data{it}.txt" 
      f_info = os.stat(data_file_path)
      it += 1
    except OSError:
      break # the name is unused

  # create data file 
  data_file = open(data_file_path, "w")

  print(f"Created data file {data_file_path}")

  print(f'Connecting to Radiacode via Bluetooth (MAC address: {BLUETOOTH_MAC})')

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
        print(v.dt.isoformat(), v)
        t = type(v)
        if t == DoseRateDB:
          data_file.write(f"DoseRateDB; {v.dt}; {v.count}; {v.count_rate}; {v.dose_rate}; {v.dose_rate_err}; {v.flags};\n")
        elif t == RareData: 
          data_file.write(f"RareData; {v.dt}; {v.duration}; {v.dose}; {v.temperature}; {v.charge_level}; {v.flags};\n")
        elif t == RealTimeData:
          data_file.write(f"RealTimeData; {v.dt}; {v.count_rate}; {v.count_rate_err}; {v.dose_rate}; {v.dose_rate_err}; {v.flags}; {v.real_time_flags};\n")
        elif t == RawData:
          data_file.write(f"RawData; {v.dt}; {v.count_rate}; {v.dose_rate};\n")
        elif t == Event: 
          data_file.write(f"Event; {v.dt}; {v.event}; {v.event_param1}; {v.flags};\n")
      if time.ticks_ms() - start > SPECTRUM_DURATION_MS:
        start = time.ticks_ms()
        # read the spectrogram 
        spectrum = rc.spectrum()
        data_file.write(f"Spectrum; {spectrum.duration}; {spectrum.a0}; {spectrum.a1}; {spectrum.a2}; {spectrum.counts};")
        print(f"{spectrum.duration} Spectrum: {spectrum}")
        # restart it 
        rc.spectrum_reset()

  except Exception: 
    # try to close data file if possible 
    try: 
      data_file.close()
    except Exception:
      pass
    continue 