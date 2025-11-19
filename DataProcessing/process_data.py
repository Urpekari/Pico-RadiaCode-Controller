"""
Takes a given text file output from the main Pico code and processes it into a CSV file for easier analysis.
"""

from datetime import datetime, timedelta
import pandas as pd
import re
import os

# get starting time stamp
starting_time_input = "2025-11-18 18:26:00"  # input("Enter the starting time stamp (YYYY-MM-DD HH:MM:SS): ")
starting_time = datetime.strptime(starting_time_input, "%Y-%m-%d %H:%M:%S")

# read data file, split into time stamped csv for data and spectrum
input_file_path = os.path.join(
    "data", "data2.txt"
)  # input("Enter the path to the input data file: ")

spectrum_output = os.path.join("output", "spectrum_data.csv")
rad_output = os.path.join("output", "rad_data.csv")
other_output = os.path.join("output", "other_data.csv")

spectrum_header = "Adj Datetime (Millis), Millis, Duration, a0, a1, a2, " + ", ".join(
    [f"Channel {x}" for x in range(0, 1024)]
)


def adjust_millis(millis_str: str) -> str:
    millis = int(millis_str)
    return (starting_time + timedelta(milliseconds=millis)).isoformat(sep=" ")


def adjust_datetime(date_str: str) -> str:
    dt = datetime.fromisoformat(date_str)
    delta = dt - datetime.fromisoformat("2021-01-01 00:00:00.000000")
    adjusted_dt = starting_time + delta
    return adjusted_dt.isoformat(sep=" ")


with (
    open(input_file_path, "r") as f,
    open(spectrum_output, "w") as f_spec,
    open(rad_output, "w") as f_rad,
    open(other_output, "w") as f_out,
):
    # write headers
    f_rad.write(
        "Adj Datetime (Millis), Adj Datetime (Datetime), Millis, Type, Datetime, Count Rate (CPS), Count Rate Err (%), Dose Rate (uSv/hr), Dose Rate Err (%), Flags, Real Time Flags, \n"
    )
    f_spec.write(spectrum_header + "\n")

    for line in f:
        elements = re.split(r";[\s]*", line)
        if elements[1] == "RealTimeData":
            f_rad.write(
                ", ".join(
                    [adjust_millis(elements[0]), adjust_datetime(elements[2])]
                    + elements
                )
                + "\n"
            )
        elif elements[1] == "RawData":
            f_rad.write(
                ", ".join(
                    [adjust_millis(elements[0]), adjust_datetime(elements[2])]
                    + [*elements[:4], "", elements[4], "", "", ""]
                )
                + "\n"
            )
        elif elements[1] == "Spectrum":
            f_spec.write(
                ", ".join(
                    [adjust_millis(elements[0])]
                    + [elements[0], *elements[2:6], elements[6][1:-1]]
                )
                + "\n"
            )
        else:
            f_out.write(line)


for c in [spectrum_output, rad_output]:
    df = pd.read_csv(c)
    print(df.head())
