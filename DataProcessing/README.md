# Data Processing
Sorting and decoding the text file created by the Pico into more usable CSVs. Also data visualization. 

### Data Entry Types: 

#### ticks_ms; **DoseRateDB**; datetime; count; count_rate; dose_rate; dose_rate_err; flags; 
* dt (datetime.datetime): Timestamp of the measurement
* count (int): Total number of counts in the measurement period
* count_rate (float): Number of counts per second
* dose_rate (float): Radiation dose rate measurement
* dose_rate_err (float): Dose rate measurement error percentage
* flags (int): Status flags for the measurement

#### ticks_ms; **RareData**; datetime; duration; dose; temperature; charge_level; flags; 
* dt (datetime.datetime): Timestamp of the status reading
* duration (int): Duration of dose accumulation in seconds
* dose (float): Accumulated radiation dose
* temperature (float): Device temperature reading
* charge_level (float): Battery charge level
* flags (int): Status flags

#### ticks_ms; **RealTimeData**; datetime; count_rate; count_rate_err; dose_rate; dose_rate_err; flags; real_time_flags; 
* dt (datetime.datetime): Timestamp of the measurement
* count_rate (float): Number of counts per second
* count_rate_err (float): Count rate error percentage
* dose_rate (int): Radiation dose rate measurement
* dose_rate_err (float): Dose rate measurement error percentage
* flags (int): Status flags for the measurement
* real_time_flags (int): Real-time status flags

#### ticks_ms; **RawData**; datetime; count_rate; dose_rate; 
* dt (datetime.datetime): Timestamp of the measurement
* count_rate (float): Number of counts per second
* dose_rate (float): Radiation dose rate measurement

#### ticks_ms; **Event**; datetime; event; event_param1; flags; 
* dt (datetime.datetime): Timestamp of the event
* event (int): Event type identifier
* event_param1 (int): Event-specific parameter
* flags (int): Event flags

### Spectrum: 
#### ticks_ms; **Spectrum**; duration; a0; a1; a2; counts; 
* duration (datetime.timedelta): Measurement duration
* a0 (float): Energy calibration coefficient (offset)
* a1 (float): Energy calibration coefficient (linear)
* a2 (float): Energy calibration coefficient (quadratic)
* counts (list[int]): List of counts per energy channel