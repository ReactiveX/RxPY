from rx import config
from rx.core import bases

from .anonymousobserver import AnonymousObserver


class BlockingObservable(bases.Observable):
    def __init__(self, observable=None):
        """Turns an observable into a blocking observable.

        Keyword arguments:
        observable -- Observable to make blocking.
        """

        self.observable = observable
        self.lock = config["concurrency"].RLock()

    def subscribe(self, observer: bases.Observer = None,
                  scheduler: bases.Scheduler = None) -> bases.Disposable:
        """Subscribe an observer to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe(observer)

        Keyword arguments:
        observer -- [Optional] The object that is to receive
            notifications.

        Return disposable object representing an observer's subscription
            to the observable sequence.
        """
        return self.observable.subscribe(observer, scheduler)

    def subscribe_callbacks(self, send=None, throw=None, close=None, scheduler=None):
        """Subscribe callbacks to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe_callbacks(send)
        3 - source.subscribe_callbacks(send, throw)
        4 - source.subscribe_callbacks(send, throw, close)

        Keyword arguments:
        send -- [Optional] Action to invoke for each element in the
            observable sequence.
        throw -- [Optional] Action to invoke upon exceptional
            termination of the observable sequence.
        close -- [Optional] Action to invoke upon graceful
            termination of the observable sequence.

        Return disposable object representing an observer's subscription
            to the observable sequence.
        """
        observer = AnonymousObserver(send, throw, close)
        return self.subscribe(observer, scheduler)

    def for_each(self, action) -> 'BlockingObservable':
        from ..operators.observable.blocking.foreach import for_each
        source = self
        return for_each(action, source)
