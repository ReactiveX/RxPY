import threading
from typing import Callable, Any

from rx.core.blockingobservable import BlockingObservable


def for_each(source: BlockingObservable,
             action: Callable[[Any], None] = None,
             action_indexed: Callable[[Any, int], None] = None) -> None:
    """Invokes a method on each item emitted by this BlockingObservable
    and blocks until the Observable completes.

    Note: This will block even if the underlying Observable is
    asynchronous.

    This is similar to Observable#subscribe(subscriber), but it blocks.
    Because it blocks it does not need the Subscriber#close() or
    Subscriber#throw(Throwable) methods. If the underlying Observable
    terminates with an error, rather than calling `onError`, this method
    will throw an exception.

    Keyword arguments:
    action -- The action to invoke for each item emitted by the
    `BlockingObservable`.

    Returns None, or raises an exception if an error occured.
    """

    latch = threading.Event()
    exception = None
    count = 0

    def send(value):
        nonlocal count, exception

        with source.lock:
            n = count
            count += 1

        if action:
            action(value)

        if action_indexed:
            action_indexed(value, n)

    def throw(error):
        nonlocal exception
        # If we receive an throw event we set the reference on the
        # outer thread so we can git it and throw after the latch.wait()
        #
        # We do this instead of throwing directly since this may be on
        # a different thread and the latch is still waiting.
        exception = error
        latch.set()

    def close():
        latch.set()

    source.observable.subscribe_(send, throw, close)

    # Block until the subscription completes and then return
    latch.wait()

    if exception is None:
        return

    raise exception if isinstance(exception, Exception) else Exception(exception)
