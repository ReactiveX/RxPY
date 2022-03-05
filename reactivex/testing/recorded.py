from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union, cast

from reactivex import Notification

if TYPE_CHECKING:
    from .reactivetest import OnErrorPredicate, OnNextPredicate


_T = TypeVar("_T")


class Recorded(Generic[_T]):
    def __init__(
        self,
        time: int,
        value: Union[Notification[_T], "OnNextPredicate[_T]", "OnErrorPredicate[_T]"],
        # comparer: Optional[typing.Comparer[_T]] = None,
    ):
        self.time = time
        self.value = value
        # self.comparer = comparer or default_comparer

    def __eq__(self, other: Any) -> bool:
        """Returns true if a recorded value matches another recorded value"""

        if isinstance(other, Recorded):
            other_ = cast(Recorded[_T], other)
            time_match = self.time == other_.time
            if not time_match:
                return False
            return self.value == other_.value

        return False

    equals = __eq__

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "%s@%s" % (self.value, self.time)
