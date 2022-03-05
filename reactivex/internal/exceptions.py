# Rx Exceptions


from typing import Optional


class SequenceContainsNoElementsError(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or "Sequence contains no elements")


class ArgumentOutOfRangeException(ValueError):
    def __init__(self, msg: Optional[str] = None):
        super(ArgumentOutOfRangeException, self).__init__(
            msg or "Argument out of range"
        )


class DisposedException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or "Object has been disposed")


class ReEntracyException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or "Re-entrancy detected")


class CompletedException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or "Observer completed")


class WouldBlockException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or "Would block")
