"""
Controller for the RadiaCode-10X Radiation Detector. Receives and stores data
from the device, takes spectrogram at set intervals. Radiacode control based on
https://github.com/cdump/radiacode
"""

import machine
import time
import os

import sdcard

from radiacode import RadiaCode
from radiacode.transports.bluetooth import DeviceNotFound as DeviceNotFoundBT
from radiacode import DoseRateDB, RareData, RawData, RealTimeData, Event

BLUETOOTH_MAC = "52:43:06:60:17:dd"
SPECTRUM_DURATION_MS = 60 * 1000
WATCHDOG_TIMEOUT = 8388


def on_wdt_reset():
    print("Watchdog reset")
    time.sleep_ms(1000)


if machine.reset_cause() == machine.WDT_RESET:
    on_wdt_reset()

led = machine.Pin("LED", machine.Pin.OUT)
# wdt = machine.WDT(timeout=WATCHDOG_TIMEOUT)


def heartbeat():
    led.toggle()
    # wdt.feed()  # reset watchdog timer


heartbeat()  # -----------------------------------------------------------------------------------------------
while True:
    print(f"Connecting to Radiacode via Bluetooth (MAC address: {BLUETOOTH_MAC})")

    heartbeat()  # ---------------------------------------------------------------------------------------------------------

    # find and connect to RadiaCode
    try:
        rc = RadiaCode(bluetooth_mac=BLUETOOTH_MAC)
    except DeviceNotFoundBT as e:
        print(e)
        continue

    heartbeat()  # ---------------------------------------------------------------------------------------------------------

    try:
        print("Setting up SD card...")
        spi = machine.SPI()
        spi.init()
        sd = sdcard.SDCard(spi, machine.Pin.board.GP17)
        print("Mounting filesystem...")
        vfs = os.VfsFat(sd)
        os.mount(vfs, "/fs")

        it = 0
        data_file_path = ""
        # find the next available data_.txt file name
        while True:
            try:
                heartbeat()  # -------------------------------------------------------------------------------------

                data_file_path = f"/fs/data{it}.txt"
                f_info = os.stat(data_file_path)
                it += 1
            except OSError:
                break  # the name is unused

        # create data file
        data_file = open(data_file_path, "a")
        data_file.close()

        print(f"Created data file {data_file_path}")
    except Exception as e:
        print("ERROR: ", e)
        continue

    heartbeat()  # ----------------------------------------------------------------------------------------------------------

    try:
        serial = rc.serial_number()
        print(f"### Serial number: {serial}")
        print("--------")

        fw_version = rc.fw_version()
        print(f"### Firmware: {fw_version}")
        print("--------")

        spectrum = rc.spectrum()
        print(f"### Spectrum: {spectrum}")
        print("--------")

        start = time.ticks_ms()
        while True:
            heartbeat()  # ----------------------------------------------------------------------------------------------------

            # infinite loop, check if there is data to process and read it if there is
            for v in rc.data_buf():
                print(v.dt.isoformat(), v)
                data_file = open(data_file_path, "a")
                data_file.write(f"{time.ticks_ms()}; ")
                t = type(v)
                # store class fields for each return option
                if t == DoseRateDB:
                    data_file.write(
                        f"DoseRateDB; {v.dt}; {v.count}; {v.count_rate}; {v.dose_rate}; {v.dose_rate_err}; {v.flags};\n"
                    )
                elif t == RareData:
                    data_file.write(
                        f"RareData; {v.dt}; {v.duration}; {v.dose}; {v.temperature}; {v.charge_level}; {v.flags};\n"
                    )
                elif t == RealTimeData:
                    data_file.write(
                        f"RealTimeData; {v.dt}; {v.count_rate}; {v.count_rate_err}; {v.dose_rate}; {v.dose_rate_err}; {v.flags}; {v.real_time_flags};\n"
                    )
                elif t == RawData:
                    data_file.write(
                        f"RawData; {v.dt}; {v.count_rate}; {v.dose_rate};\n"
                    )
                elif t == Event:
                    print("fake write")
                    # data_file.write(
                    #     f"Event; {v.dt}; {v.event.name}; {v.event_param1}; {v.flags};\n"
                    # )
                # flush and close to reduce caching
                data_file.flush()
                data_file.close()
            if time.ticks_ms() - start > SPECTRUM_DURATION_MS:
                heartbeat()  # ---------------------------------------------------------------------------------------------------

                start = time.ticks_ms()
                # read the spectrogram
                spectrum = rc.spectrum()

                data_file = open(data_file_path, "a")
                data_file.write(
                    f"{time.ticks_ms()}; Spectrum; {spectrum.duration}; {spectrum.a0}; {spectrum.a1}; {spectrum.a2}; {spectrum.counts};\n"
                )
                data_file.flush()
                data_file.close()

                print(f"{spectrum.duration} Spectrum: {spectrum}")
                # restart it
                # rc.spectrum_reset()
    except Exception:
        # try to close data file if possible
        try:
            data_file.close()
        except Exception:
            pass

        machine.reset()
        continue
