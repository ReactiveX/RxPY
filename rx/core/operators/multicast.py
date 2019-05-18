from typing import Union, Callable, Optional

from rx.core import Observable, ConnectableObservable
from rx.core.typing import Subject, Mapper, Scheduler
from rx.disposable import CompositeDisposable


def _multicast(subject: Optional[Subject] = None,
               subject_factory: Optional[Callable[[Optional[Scheduler]], Subject]] = None,
               mapper: Optional[Callable[[ConnectableObservable], Observable]] = None
               ) -> Callable[[Observable], Union[Observable, ConnectableObservable]]:
    """Multicasts the source sequence notifications through an
    instantiated subject into all uses of the sequence within a mapper
    function. Each subscription to the resulting sequence causes a
    separate multicast invocation, exposing the sequence resulting from
    the mapper function's invocation. For specializations with fixed
    subject types, see Publish, PublishLast, and Replay.

    Examples:
        >>> res = multicast(observable)
        >>> res = multicast(subject_factory=lambda scheduler: Subject(), mapper=lambda x: x)

    Args:
        subject_factory: Factory function to create an intermediate
            subject through which the source sequence's elements will be
            multicast to the mapper function.
        subject: Subject to push source elements into.
        mapper: [Optional] Mapper function which can use the
            multicasted source sequence subject to the policies enforced
            by the created subject. Specified only if subject_factory" is a
            factory function.

    Returns:
        An observable sequence that contains the elements of a sequence
        produced by multicasting the source sequence within a mapper
        function.
    """

    def multicast(source: Observable) -> Union[Observable, ConnectableObservable]:
        if subject_factory:
            def subscribe(observer, scheduler=None):
                connectable = source.pipe(_multicast(subject=subject_factory(scheduler)))
                subscription = mapper(connectable).subscribe(observer, scheduler=scheduler)

                return CompositeDisposable(subscription, connectable.connect(scheduler))
            return Observable(subscribe)
        return ConnectableObservable(source, subject)
    return multicast
