from rx.core.blockingobservable import BlockingObservable
from rx.internal.utils import adapt_call
from rx import config


def for_each(action, source: BlockingObservable):
    """Invokes a method on each item emitted by this BlockingObservable and
    blocks until the Observable completes.

    Note: This will block even if the underlying Observable is asynchronous.

    This is similar to Observable#subscribe(subscriber), but it blocks. Because
    it blocks it does not need the Subscriber#close() or
    Subscriber#throw(Throwable) methods. If the underlying Observable
    terminates with an error, rather than calling `onError`, this method will
    throw an exception.

    Keyword arguments:
    :param types.FunctionType action: the action to invoke for each item
        emitted by the `BlockingObservable`.
    :raises Exception: if an error occurs
    :returns: None
    :rtype: None
    """

    action = adapt_call(action)
    latch = config["concurrency"].Event()
    exception = [None]
    count = [0]

    def send(value):
        with source.lock:
            n = count[0]
            count[0] += 1
        action(value, n)

    def throw(err):
        # If we receive an throw event we set the reference on the
        # outer thread so we can git it and throw after the latch.wait()
        #
        # We do this instead of throwing directly since this may be on
        # a different thread and the latch is still waiting.
        exception[0] = err
        latch.set()

    def close():
        latch.set()

    source.observable.subscribe_callbacks(send, throw, close)

    # Block until the subscription completes and then return
    latch.wait()

    if exception[0] is not None:
        raise Exception(exception[0])
