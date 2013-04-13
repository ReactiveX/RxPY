# Rx Exceptions

class SequenceContainsNoElementsError(Exception):
    def __init__(self, arg=None):
        self.args = arg or "Sequence contains no elements"

class ArgumentOutOfRangeException(ValueError):
    def __init__(self, arg=None):
        self.args = arg or "Argument out of range"

class DisposedException(Exception):
    def __init__(self, arg=None):
        self.args = arg or "Object has been disposed"