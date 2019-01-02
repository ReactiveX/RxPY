from typing import Union, Callable

from rx.core import ObservableBase, AnonymousObservable, ConnectableObservable
from rx.core.typing import Subject, Mapper
from rx.disposables import CompositeDisposable


def multicast(source: ObservableBase, subject: Subject = None,
              subject_factory: Callable[[], Subject] = None,
              mapper: Mapper = None) -> Union[ObservableBase, ConnectableObservable]:
    """Multicasts the source sequence notifications through an
    instantiated subject into all uses of the sequence within a mapper
    function. Each subscription to the resulting sequence causes a
    separate multicast invocation, exposing the sequence resulting from
    the mapper function's invocation. For specializations with fixed
    subject types, see Publish, PublishLast, and Replay.

    Example:
    1 - res = source.multicast(observable)
    2 - res = source.multicast(subject_factory=lambda scheduler: Subject(),
                               mapper=lambda x: x)

    Keyword arguments:
    subject_factory -- Factory function to create an intermediate
        subject through which the source sequence's elements will be
        multicast to the mapper function.
    subject -- Subject to push source elements into.
    mapper -- [Optional] Optional mapper function which can use the
        multicasted source sequence subject to the policies enforced
        by the created subject. Specified only if subject_factory" is a
        factory function.

    Returns an observable sequence that contains the elements of a
    sequence produced by multicasting the source sequence within a
    mapper function.
    """

    if subject_factory:
        def subscribe(observer, scheduler=None):
            connectable = source.multicast(subject=subject_factory(scheduler))
            subscription = mapper(connectable).subscribe(observer, scheduler)

            return CompositeDisposable(subscription, connectable.connect(scheduler))
        return AnonymousObservable(subscribe)

    return ConnectableObservable(source, subject)
