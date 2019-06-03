from typing import Callable, Optional

from rx import operators as ops
from rx.core import Observable, ConnectableObservable, pipe
from rx.core.typing import Mapper
from rx.subject import Subject


def _publish(mapper: Optional[Mapper] = None) -> Callable[[Observable], ConnectableObservable]:
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
        return pipe(ops.multicast(subject_factory=lambda _: Subject(), mapper=mapper))

    return pipe(ops.multicast(subject=Subject()))


def _share() -> Callable[[Observable], Observable]:
    """Share a single subscription among multple observers.

    Returns a new Observable that multicasts (shares) the original
    Observable. As long as there is at least one Subscriber this
    Observable will be subscribed and emitting data. When all
    subscribers have unsubscribed it will unsubscribe from the source
    Observable.

    This is an alias for a composed publish() and ref_count().
    """
    return pipe(_publish(), ops.ref_count())
