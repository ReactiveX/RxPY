from typing import Any, Callable
from threading import RLock

from rx.core import abc
from rx.internal import Iterable

from .anonymousobserver import AnonymousObserver


class BlockingObservable(abc.Observable):
    def __init__(self, observable=None):
        """Turns an observable into a blocking observable.

        Keyword arguments:
        observable -- Observable to make blocking.
        """

        self.observable = observable
        self.lock = RLock()

    def subscribe(self, observer: abc.Observer = None,
                  scheduler: abc.Scheduler = None) -> abc.Disposable:
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

    def __iter__(self):
        """Returns an iterator that can iterate over items emitted by
        this `BlockingObservable`.
        """

        return iter(self.to_iterable())

    def first(self) -> Any:
        """
        Blocks until the first element emits from a BlockingObservable.

        If no item is emitted when close() is called, an exception is
        thrown

        Note: This will block even if the underlying Observable is
        asynchronous.

        Keyword arguments:
        source -- Blocking observable sequence.

        Returns the first item to be emitted from the blocking
        observable.
        """
        from ..operators.observable.blocking.first import first
        source = self
        return first(source)

    def first_or_default(self, default_value: Any) -> Any:
        """
        Blocks until the first element emits from a BlockingObservable.

        If no item is emitted when close() is called, the provided
        default value is returned instead

        Note: This will block even if the underlying Observable is
        asynchronous.

        Keyword arguments:
        source -- Blocking observable sequence.
        default_value -- Default value to use

        Returns the first item to be emitted from the blocking
        observable.
        """
        from ..operators.observable.blocking.first import first_or_default
        source = self
        return first_or_default(source, default_value)

    def for_each(self, action: Callable[[Any], None] = None,
                 action_indexed: Callable[[Any, int], None] = None) -> None:
        """Invokes a method on each item emitted by this
        BlockingObservable and blocks until the Observable completes.

        Note: This will block even if the underlying Observable is
        asynchronous.

        This is similar to Observable#subscribe(subscriber), but it
        blocks. Because it blocks it does not need the
        Subscriber#close() or Subscriber#throw(Throwable) methods. If
        the underlying Observable terminates with an error, rather than
        calling `onError`, this method will throw an exception.

        Keyword arguments:
        action -- The action to invoke for each item emitted by the
        `BlockingObservable`.

        Returns None, or raises an exception if an error occured.
        """
        from ..operators.observable.blocking.foreach import for_each
        return for_each(self, action, action_indexed)

    def last(self) -> Any:
        """Blocks until the last element emits from a
        BlockingObservable.

        If no item is emitted when close() is called, an exception is
        thrown

        Note: This will block even if the underlying Observable is
        asynchronous.

        Returns the last item to be emitted from a BlockingObservable
        """
        from ..operators.observable.blocking.last import last
        source = self
        return last(source)

    def last_or_default(self, default_value: Any) -> Any:
        """Blocks until the last element emits from a
        BlockingObservable.

        If no item is emitted when close() is called, the provided
        default_value will be returned

        Note: This will block even if the underlying Observable is
        asynchronous.

        Keyword arguments:
        default_value -- Value to return if no value has been emitted.

        Returns the last item to be emitted from a BlockingObservable
        """
        from ..operators.observable.blocking.last import last_or_default
        source = self
        return last_or_default(source, default_value)

    def to_marbles_blocking(self, scheduler=None):
        """Convert an observable sequence into a marble diagram string

        Keyword arguments:
        scheduler -- [Optional] The scheduler used to run the the input
            sequence on.

        Returns marble string.
        """
        from ..testing.marbles import to_marbles_blocking
        return to_marbles_blocking(self, scheduler)

    def to_iterable(self) -> Iterable:
        """Returns an iterator that can iterate over items emitted by
        this `BlockingObservable`.

        Returns an iterable that can iterate over the items emitted by
        this `BlockingObservable`.
        """
        from ..operators.observable.blocking.toiterable import to_iterable
        return to_iterable(self)
