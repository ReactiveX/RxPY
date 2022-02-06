from typing import Any, TypeVar, Generic, Optional, cast

from rx.core import typing, Notification
from rx.internal.basic import default_comparer

_T = TypeVar("_T")


class Recorded(Generic[_T]):
    def __init__(
        self,
        time: int,
        value: Notification[_T],
        comparer: Optional[typing.Comparer[_T]] = None,
    ):
        self.time = time
        self.value = value
        self.comparer = comparer or default_comparer

    def __eq__(self, other: Any) -> bool:
        """Returns true if a recorded value matches another recorded value"""

        if isinstance(other, Recorded):
            time_match = self.time == other.time
            return time_match and self.comparer(
                self.value, cast(Recorded[_T], other).value
            )

        return False

    equals = __eq__

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "%s@%s" % (self.value, self.time)
