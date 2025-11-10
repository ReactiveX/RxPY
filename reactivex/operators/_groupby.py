from collections.abc import Callable
from typing import Any, TypeVar

from reactivex import GroupedObservable, Observable, typing
from reactivex.internal import curry_flip
from reactivex.subject import Subject

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")

# pylint: disable=import-outside-toplevel


@curry_flip
def group_by_(
    source: Observable[_T],
    key_mapper: typing.Mapper[_T, _TKey],
    element_mapper: typing.Mapper[_T, _TValue] | None = None,
    subject_mapper: Callable[[], Subject[_TValue]] | None = None,
) -> Observable[GroupedObservable[_TKey, _TValue]]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function.

    Examples:
        >>> res = source.pipe(group_by(lambda x: x.id))
        >>> res = group_by(lambda x: x.id)(source)

    Args:
        source: Source observable to group.
        key_mapper: A function to extract the key for each element.
        element_mapper: Optional function to map elements to values.
        subject_mapper: Optional function that returns a subject used to initiate
            a grouped observable.

    Returns:
        An observable sequence of grouped observables.
    """
    from reactivex import operators as ops

    def duration_mapper(_: GroupedObservable[Any, Any]) -> Observable[Any]:
        import reactivex

        return reactivex.never()

    return source.pipe(
        ops.group_by_until(key_mapper, element_mapper, duration_mapper, subject_mapper)
    )


__all__ = ["group_by_"]
