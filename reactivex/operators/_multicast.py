from typing import Callable, Optional, TypeVar, Union

from reactivex import ConnectableObservable, Observable, abc
from reactivex import operators as ops
from reactivex.disposable import CompositeDisposable

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


def multicast_(
    subject: Optional[abc.SubjectBase[_TSource]] = None,
    *,
    subject_factory: Optional[
        Callable[[Optional[abc.SchedulerBase]], abc.SubjectBase[_TSource]]
    ] = None,
    mapper: Optional[Callable[[Observable[_TSource]], Observable[_TResult]]] = None,
) -> Callable[
    [Observable[_TSource]], Union[Observable[_TResult], ConnectableObservable[_TSource]]
]:
    """Multicasts the source sequence notifications through an
    instantiated subject into all uses of the sequence within a mapper
    function. Each subscription to the resulting sequence causes a
    separate multicast invocation, exposing the sequence resulting from
    the mapper function's invocation. For specializations with fixed
    subject types, see Publish, PublishLast, and Replay.

    Examples:
        >>> res = multicast(observable)
        >>> res = multicast(
            subject_factory=lambda scheduler: Subject(),
            mapper=lambda x: x
        )

    Args:
        subject_factory: Factory function to create an intermediate
            subject through which the source sequence's elements will be
            multicast to the mapper function.
        subject: Subject to push source elements into.
        mapper: [Optional] Mapper function which can use the
            multicasted source sequence subject to the policies enforced
            by the created subject. Specified only if subject_factory"
            is a factory function.

    Returns:
        An observable sequence that contains the elements of a sequence
        produced by multicasting the source sequence within a mapper
        function.
    """

    def multicast(
        source: Observable[_TSource],
    ) -> Union[Observable[_TResult], ConnectableObservable[_TSource]]:
        if subject_factory:

            def subscribe(
                observer: abc.ObserverBase[_TResult],
                scheduler: Optional[abc.SchedulerBase] = None,
            ) -> abc.DisposableBase:
                assert subject_factory
                connectable = source.pipe(
                    ops.multicast(subject=subject_factory(scheduler))
                )
                assert mapper
                subscription = mapper(connectable).subscribe(
                    observer, scheduler=scheduler
                )

                return CompositeDisposable(subscription, connectable.connect(scheduler))

            return Observable(subscribe)

        if not subject:
            raise ValueError("multicast: Subject cannot be None")
        ret: ConnectableObservable[_TSource] = ConnectableObservable(source, subject)
        return ret

    return multicast
