from typing import Callable, Optional, TypeVar

from rx import operators
from rx.core import Observable
from rx.core.typing import Mapper

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


class AverageValue(object):
    def __init__(self, sum: float, count: int):
        self.sum = sum
        self.count = count


def average(
    key_mapper: Optional[Mapper[_T, _TKey]] = None,
) -> Callable[[Observable[_T]], Observable[float]]:
    def average(source: Observable[_T]) -> Observable[float]:
        """Partially applied average operator.

        Computes the average of an observable sequence of values that
        are in the sequence or obtained by invoking a transform
        function on each element of the input sequence if present.

        Examples:
            >>> res = average(source)

        Args:
            source: Source observable to average.

        Returns:
            An observable sequence containing a single element with the
            average of the sequence of values.
        """

        if key_mapper:
            return source.pipe(
                operators.map(key_mapper),
                operators.average(),
            )

        def accumulator(prev: AverageValue, cur: float) -> AverageValue:
            return AverageValue(sum=prev.sum + cur, count=prev.count + 1)

        def mapper(s: AverageValue) -> float:
            if s.count == 0:
                raise Exception("The input sequence was empty")

            return s.sum / float(s.count)

        seed = AverageValue(sum=0, count=0)
        return source.pipe(
            operators.scan(accumulator, seed),
            operators.last(),
            operators.map(mapper),
        )

    return average


__all__ = ["average"]
