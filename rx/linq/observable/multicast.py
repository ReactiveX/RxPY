from rx import Observable, AnonymousObservable
from rx.linq.connectableobservable import ConnectableObservable
from rx.disposables import CompositeDisposable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def multicast(self, stream=None, stream_selector=None, selector=None):
    """Multicasts the source sequence notifications through an instantiated
    stream into all uses of the sequence within a selector function. Each
    subscription to the resulting sequence causes a separate multicast
    invocation, exposing the sequence resulting from the selector function's
    invocation. For specializations with fixed stream types, see Publish,
    PublishLast, and Replay.

    Example:
    1 - res = source.multicast(observable)
    2 - res = source.multicast(stream_selector=lambda: Stream(),
                               selector=lambda x: x)

    Keyword arguments:
    stream_selector -- {Function} Factory function to create an
        intermediate stream through which the source sequence's elements
        will be multicast to the selector function.
    stream -- Stream {Stream} to push source elements into.
    selector -- {Function} [Optional] Optional selector function which can
        use the multicasted source sequence stream to the policies enforced
        by the created stream. Specified only if stream_selector" is a
        factory function.

    Returns an observable {Observable} sequence that contains the elements
    of a sequence produced by multicasting the source sequence within a
    selector function.
    """

    source = self
    if stream_selector:
        def subscribe(observer):
            connectable = source.multicast(stream=stream_selector())
            return CompositeDisposable(selector(connectable).subscribe(observer), connectable.connect())

        return AnonymousObservable(subscribe)
    else:
        return ConnectableObservable(source, stream)
