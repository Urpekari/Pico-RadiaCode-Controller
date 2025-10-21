import utime

class timedelta:
  def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    self.days = int(days) + int(weeks) * 7 
    self.seconds = (int(hours) * 60 + int(minutes)) * 60 + int(seconds)
    self.microseconds = int(microseconds)
    self.milliseconds = int(milliseconds)

  def total_seconds(self):
    return self.days * 86400 + self.seconds + self.milliseconds / 1_000 + self.microseconds / 1_000_000

  def __add__(self, other):
    if isinstance(other, datetime):
      return other + self
    raise TypeError("unsupported operand type(s) for +: 'timedelta' and '{}'".format(type(other)))


  def __sub__(self, other):
    if isinstance(other, timedelta):
      # naive subtraction (not normalizing)
      return timedelta(seconds=int(self.total_seconds() - other.total_seconds()))
    raise TypeError("unsupported operand for -")

  def __repr__(self):
    return "timedelta(seconds={})".format(int(self.total_seconds()))


class datetime: # type: ignore

  def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0):
    self._ts = utime.mktime((year, month, day, hour, minute, second, 0, 0))
    self.year = year
    self.month = month
    self.day = day
    self.hour = hour 
    self.minute = minute 
    self.second = second 

  @classmethod 
  def fromtimestamp(cls, ts, tz=None):
    obj = cls.__new__(cls)
    obj._ts = ts
    obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, _, _ = utime.localtime(ts)
    return obj 
   
  @classmethod
  def now(cls, tz=None):
    obj = cls.__new__(cls)
    obj.load_utime()

    return obj

  def load_utime(self):
    self._ts = utime.time()

  def timestamp(self):
    return self._ts
  
  def __add__(self, td):
    if not isinstance(td, timedelta):
      raise TypeError("can only add timedelta to datetime")
    return datetime.fromtimestamp(self._ts + int(td.total_seconds()))
  
  def __sub__(self, other):
    if isinstance(other, timedelta):
      return datetime.fromtimestamp(self._ts - int(other.total_seconds()))
    if isinstance(other, datetime):
      return timedelta(seconds=int(self._ts - other._ts))
    raise TypeError("unsupported operand types for -")

  def __repr__(self):
    return "<datetime {}>".format(self.isoformat())

