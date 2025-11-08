from collections.abc import Callable
from typing import TypeVar

from reactivex import ConnectableObservable, Observable, abc, typing
from reactivex import operators as ops
from reactivex.subject import ReplaySubject
from reactivex.typing import Mapper

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


def replay_(
    mapper: Mapper[Observable[_TSource], Observable[_TResult]] | None = None,
    buffer_size: int | None = None,
    window: typing.RelativeTime | None = None,
    scheduler: abc.SchedulerBase | None = None,
) -> Callable[
    [Observable[_TSource]], Observable[_TResult] | ConnectableObservable[_TSource]
]:
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence replaying notifications
    subject to a maximum time length for the replay buffer.

    This operator is a specialization of Multicast using a
    ReplaySubject.

    Examples:
        >>> res = replay(buffer_size=3)
        >>> res = replay(buffer_size=3, window=500)
        >>> res = replay(None, 3, 500)
        >>> res = replay(lambda x: x.take(6).repeat(), 3, 500)

    Args:
        mapper: [Optional] Selector function which can use the multicasted
            source sequence as many times as needed, without causing
            multiple subscriptions to the source sequence. Subscribers to
            the given source will receive all the notifications of the
            source subject to the specified replay buffer trimming policy.
        buffer_size: [Optional] Maximum element count of the replay
            buffer.
        window: [Optional] Maximum time length of the replay buffer.
        scheduler: [Optional] Scheduler the observers are invoked on.

    Returns:
        An observable sequence that contains the elements of a
    sequence produced by multicasting the source sequence within a
    mapper function.
    """

    if mapper:

        def subject_factory(
            scheduler: abc.SchedulerBase | None = None,
        ) -> ReplaySubject[_TSource]:
            return ReplaySubject(buffer_size, window, scheduler)

        return ops.multicast(subject_factory=subject_factory, mapper=mapper)
    rs: ReplaySubject[_TSource] = ReplaySubject(buffer_size, window, scheduler)
    return ops.multicast(subject=rs)


__all__ = ["replay_"]
