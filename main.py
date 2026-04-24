"""
Controller for the RadiaCode-10X Radiation Detector. Receives and stores data
from the device, takes spectrogram at set intervals. Radiacode control based on
https://github.com/cdump/radiacode
"""

import machine
import time

from radiacode import RadiaCode
from radiacode.transports.bluetooth import DeviceNotFound as DeviceNotFoundBT
from radiacode import DoseRateDB, RareData, RawData, RealTimeData, Event

BLUETOOTH_MAC = "52:43:06:60:33:12"
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

            # infinite loop, check if there is data to process and print it
            for v in rc.data_buf():
                print(v.dt.isoformat(), v)
                t = type(v)
                # print class fields for each return option
                if t == DoseRateDB:
                    print(
                        f"DoseRateDB; {v.dt}; {v.count}; {v.count_rate}; {v.dose_rate}; {v.dose_rate_err}; {v.flags};"
                    )
                elif t == RareData:
                    print(
                        f"RareData; {v.dt}; {v.duration}; {v.dose}; {v.temperature}; {v.charge_level}; {v.flags};"
                    )
                elif t == RealTimeData:
                    print(
                        f"RealTimeData; {v.dt}; {v.count_rate}; {v.count_rate_err}; {v.dose_rate}; {v.dose_rate_err}; {v.flags}; {v.real_time_flags};"
                    )
                elif t == RawData:
                    print(
                        f"RawData; {v.dt}; {v.count_rate}; {v.dose_rate};"
                    )
                elif t == Event:
                    print("fake print")
                    # print(
                    #     f"Event; {v.dt}; {v.event.name}; {v.event_param1}; {v.flags};"
                    # )
            if time.ticks_ms() - start > SPECTRUM_DURATION_MS:
                heartbeat()  # ---------------------------------------------------------------------------------------------------

                start = time.ticks_ms()
                # read the spectrogram
                spectrum = rc.spectrum()

                print(
                    f"{time.ticks_ms()}; Spectrum; {spectrum.duration}; {spectrum.a0}; {spectrum.a1}; {spectrum.a2}; {spectrum.counts};"
                )

                print(f"{spectrum.duration} Spectrum: {spectrum}")
                # restart it
                # rc.spectrum_reset()
    except Exception as e:
        print("ERROR: ", e)
        machine.reset()
        continue