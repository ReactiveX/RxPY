from collections.abc import Callable
from typing import TypeVar

from reactivex import ConnectableObservable, Observable, abc
from reactivex import operators as ops
from reactivex.subject import BehaviorSubject
from reactivex.typing import Mapper

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def publish_value_(
    initial_value: _T1,
    mapper: Mapper[Observable[_T1], Observable[_T2]] | None = None,
) -> (
    Callable[[Observable[_T1]], ConnectableObservable[_T1]]
    | Callable[[Observable[_T1]], Observable[_T2]]
):
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence and starts with *initial_value*.

    This operator is a specialization of :func:`multicast` using a
    :class:`~reactivex.subject.BehaviorSubject`.

    Args:
        initial_value: The value received by observers upon subscription
            before the source emits its first element.
        mapper: [Optional] Selector function which can use the multicasted
            source sequence as many times as needed, without causing multiple
            subscriptions to the source sequence.

    Returns:
        When *mapper* is omitted: a
        :class:`~reactivex.ConnectableObservable` backed by a
        :class:`~reactivex.subject.BehaviorSubject` seeded with
        *initial_value*.  When *mapper* is provided: an observable
        sequence that contains the elements of a sequence produced by
        multicasting the source sequence within the mapper function.
    """
    if mapper:

        def subject_factory(
            scheduler: abc.SchedulerBase | None = None,
        ) -> BehaviorSubject[_T1]:
            return BehaviorSubject(initial_value)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)

    subject = BehaviorSubject(initial_value)
    return ops.multicast(subject)


__all__ = ["publish_value_"]
