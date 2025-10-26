# type: ignore
def dataclass(_cls=None, *, init=True, repr=True, eq=True):
    # print(type(_cls))
    def wrap(cls):
        fields = getattr(cls, "__annotations__", {})  # cls.__annotations__

        if init:

            def __init__(self, **kwargs):
                for name, value in kwargs.items():
                    setattr(self, name, value)

            cls.__init__ = __init__

        if repr:

            def __repr__(self):
                values = ", ".join(f"{k}={getattr(self, k)!r}" for k in fields)
                return f"{cls.__name__}({values})"

            cls.__repr__ = __repr__

        if eq:

            def __eq__(self, other):
                for k in fields:
                    if getattr(self, k) != getattr(other, k):
                        return False

                return True

            cls.__eq__ = __eq__

        return cls

    if _cls is None:
        return wrap
    else:
        return wrap(_cls)
