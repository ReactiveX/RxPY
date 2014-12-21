import threading

from rx.blockingobservable import BlockingObservable
from rx.internal import extensionmethod

@extensionmethod(BlockingObservable)
def for_each(self, action):
    """Invokes a method on each item emitted by this BlockingObservable and
    blocks until the Observable completes.

    Note: This will block even if the underlying Observable is asynchronous.

    This is similar to Observable#subscribe(Subscriber), but it blocks. Because
    it blocks it does not need the Subscriber#onCompleted() or
    Subscriber#onError(Throwable) methods. If the underlying Observable
    terminates with an error, rather than calling `onError`, this method will
    throw an exception.

    Keyword parameters:
    :param types.FunctionType action: the action to invoke for each item
        emitted by the `BlockingObservable`.
    :raises Exception: if an error occurs
    :returns: None
    :rtype: None
    """

    latch = threading.Event()
    exception = None

    def on_next(value):
        action(value)

    def on_error(err):
        # If we receive an onError event we set the reference on the
        # outer thread so we can git it and throw after the latch.wait()
        #
        # We do this instead of throwing directly since this may be on
        # a different thread and the latch is still waiting.
        exception = err
        latch.set()

    def on_completed():
        latch.set()

    self.observable.subscribe(_on_next, on_error, on_completed)

    # block until the subscription completes and then return
    latch.wait()

    if exception is not None:
        raise exception
