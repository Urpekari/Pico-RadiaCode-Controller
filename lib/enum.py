class Enum:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.value == self.value

    def __hash__(self):
        return hash(self.value)
