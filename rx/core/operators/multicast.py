from typing import Callable, Optional, TypeVar, Union

from rx.core import ConnectableObservable, Observable, abc
from rx.disposable import CompositeDisposable

_T = TypeVar("_T")


def multicast_(
    subject: Optional[abc.SubjectBase[_T]] = None,
    subject_factory: Optional[
        Callable[[Optional[abc.SchedulerBase]], abc.SubjectBase[_T]]
    ] = None,
    mapper: Optional[Callable[[ConnectableObservable[_T]], Observable[_T]]] = None,
) -> Callable[[Observable[_T]], Union[Observable[_T], ConnectableObservable[_T]]]:
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

    def multicast(
        source: Observable[_T],
    ) -> Union[Observable[_T], ConnectableObservable[_T]]:
        if subject_factory:

            def subscribe(
                observer: abc.ObserverBase[_T],
                scheduler: Optional[abc.SchedulerBase] = None,
            ) -> abc.DisposableBase:
                connectable = source.pipe(
                    multicast_(subject=subject_factory(scheduler))
                )
                assert mapper
                subscription = mapper(connectable).subscribe(
                    observer, scheduler=scheduler
                )

                return CompositeDisposable(subscription, connectable.connect(scheduler))

            return Observable(subscribe)
        ret: ConnectableObservable[_T] = ConnectableObservable(source, subject)
        return ret

    return multicast
