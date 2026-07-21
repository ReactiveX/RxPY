from typing import TypeVar

from reactivex import ConnectableObservable, Observable, abc, compose
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.subject import Subject
from reactivex.typing import Mapper

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


@curry_flip
def publish_(
    source: Observable[_TSource],
    mapper: Mapper[Observable[_TSource], Observable[_TResult]] | None = None,
) -> Observable[_TResult] | ConnectableObservable[_TSource]:
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence. This operator is a
    specialization of Multicast using a regular Subject.

    Examples:
        >>> source.pipe(publish())
        >>> source.pipe(publish(lambda x: x))
        >>> publish()(source)

    Args:
        source: Source observable to publish.
        mapper: [Optional] Selector function which can use the
            multicasted source sequence as many times as needed, without
            causing multiple subscriptions to the source sequence.

    Returns:
        An observable sequence that contains the elements of a sequence
        produced by multicasting the source sequence within a mapper
        function.
    """

    if mapper:

        def factory(scheduler: abc.SchedulerBase | None = None) -> Subject[_TSource]:
            return Subject()

        return source.pipe(ops.multicast(subject_factory=factory, mapper=mapper))

    subject: Subject[_TSource] = Subject()
    return source.pipe(ops.multicast(subject=subject))


@curry_flip
def share_(source: Observable[_TSource]) -> Observable[_TSource]:
    """Share a single subscription among multiple observers.

    Returns a new Observable that multicasts (shares) the original
    Observable. As long as there is at least one Subscriber this
    Observable will be subscribed and emitting data. When all
    subscribers have unsubscribed it will unsubscribe from the source
    Observable.

    This is an alias for a composed publish() and ref_count().

    Examples:
        >>> source.pipe(share())
        >>> share()(source)

    Args:
        source: Source observable to share.

    Returns:
        An observable that shares a single subscription.
    """
    return source.pipe(
        compose(
            ops.publish(),
            ops.ref_count(),
        )
    )


__all__ = ["publish_", "share_"]
