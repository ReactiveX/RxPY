from rx.core import ObservableBase, AnonymousObservable
from rx.operators.connectableobservable import ConnectableObservable
from rx.disposables import CompositeDisposable


def multicast(source: ObservableBase, subject=None, subject_selector=None, selector=None) -> ObservableBase:
    """Multicasts the source sequence notifications through an instantiated
    subject into all uses of the sequence within a selector function. Each
    subscription to the resulting sequence causes a separate multicast
    invocation, exposing the sequence resulting from the selector function's
    invocation. For specializations with fixed subject types, see Publish,
    PublishLast, and Replay.

    Example:
    1 - res = source.multicast(observable)
    2 - res = source.multicast(subject_selector=lambda scheduler: Subject(),
                               selector=lambda x: x)

    Keyword arguments:
    subject_selector -- Factory function to create an intermediate
        subject through which the source sequence's elements will be
        multicast to the selector function.
    subject -- Subject to push source elements into.
    selector -- [Optional] Optional selector function which can use the
        multicasted source sequence subject to the policies enforced
        by the created subject. Specified only if subject_selector" is a
        factory function.

    Returns an observable sequence that contains the elements of a
    sequence produced by multicasting the source sequence within a
    selector function.
    """

    if subject_selector:
        def subscribe(observer, scheduler=None):
            connectable = source.multicast(subject=subject_selector(scheduler))
            return CompositeDisposable(selector(connectable).subscribe(observer, scheduler), connectable.connect(scheduler))
        return AnonymousObservable(subscribe)

    return ConnectableObservable(source, subject)
