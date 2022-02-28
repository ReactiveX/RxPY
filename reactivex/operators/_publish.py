from typing import Callable, Optional, TypeVar, Union

from reactivex import ConnectableObservable, Observable, abc, compose
from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.typing import Mapper

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


def publish_(
    mapper: Optional[Mapper[Observable[_TSource], Observable[_TResult]]] = None,
) -> Callable[
    [Observable[_TSource]], Union[Observable[_TResult], ConnectableObservable[_TSource]]
]:
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence. This operator is a
    specialization of Multicast using a regular Subject.

    Example:
        >>> res = publish()
        >>> res = publish(lambda x: x)

    mapper: [Optional] Selector function which can use the
        multicasted source sequence as many times as needed, without causing
        multiple subscriptions to the source sequence. Subscribers to the
        given source will receive all notifications of the source from the
        time of the subscription on.

    Returns:
        An observable sequence that contains the elements of a sequence
        produced by multicasting the source sequence within a mapper
        function.
    """

    if mapper:

        def factory(scheduler: Optional[abc.SchedulerBase] = None) -> Subject[_TSource]:
            return Subject()

        return ops.multicast(subject_factory=factory, mapper=mapper)

    subject: Subject[_TSource] = Subject()
    return ops.multicast(subject=subject)


def share_() -> Callable[[Observable[_TSource]], Observable[_TSource]]:
    """Share a single subscription among multple observers.

    Returns a new Observable that multicasts (shares) the original
    Observable. As long as there is at least one Subscriber this
    Observable will be subscribed and emitting data. When all
    subscribers have unsubscribed it will unsubscribe from the source
    Observable.

    This is an alias for a composed publish() and ref_count().
    """
    return compose(
        ops.publish(),
        ops.ref_count(),
    )


__all__ = ["publish_", "share_"]
