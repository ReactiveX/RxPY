from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, cast

from reactivex import Observable, operators, typing

_T = TypeVar("_T")


@dataclass
class AverageValue:
    sum: float
    count: int


def average_(
    key_mapper: Optional[typing.Mapper[_T, float]] = None,
) -> Callable[[Observable[_T]], Observable[float]]:
    def average(source: Observable[Any]) -> Observable[float]:
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

        key_mapper_: typing.Mapper[_T, float] = key_mapper or (
            lambda x: float(cast(Any, x))
        )

        def accumulator(prev: AverageValue, cur: float) -> AverageValue:
            return AverageValue(sum=prev.sum + cur, count=prev.count + 1)

        def mapper(s: AverageValue) -> float:
            if s.count == 0:
                raise Exception("The input sequence was empty")

            return s.sum / float(s.count)

        seed = AverageValue(sum=0, count=0)

        ret = source.pipe(
            operators.map(key_mapper_),
            operators.scan(accumulator, seed),
            operators.last(),
            operators.map(mapper),
        )
        return ret

    return average


__all__ = ["average_"]
