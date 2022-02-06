# Rx Exceptions


from typing import Optional


class SequenceContainsNoElementsError(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(SequenceContainsNoElementsError, self).__init__(
            msg or "Sequence contains no elements"
        )


class ArgumentOutOfRangeException(ValueError):
    def __init__(self, msg: Optional[str] = None):
        super(ArgumentOutOfRangeException, self).__init__(
            msg or "Argument out of range"
        )


class DisposedException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(DisposedException, self).__init__(msg or "Object has been disposed")


class ReEntracyException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(ReEntracyException, self).__init__(msg or "Re-entrancy detected")


class CompletedException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(CompletedException, self).__init__(msg or "Observer completed")


class WouldBlockException(Exception):
    def __init__(self, msg: Optional[str] = None):
        super(WouldBlockException, self).__init__(msg or "Would block")
