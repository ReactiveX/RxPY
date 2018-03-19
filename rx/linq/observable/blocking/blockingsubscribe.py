from rx.core.blockingobservable import BlockingObservable
from rx.internal import extensionmethod
from rx import config

@extensionmethod(BlockingObservable)
def blocking_subscribe(source, on_next = None, on_error = None, on_completed = None):
    """ 
    Blocks until all the items are emitted from a BlockingObservable until 
    the on_completed() is called.
    
    source: Source observable sequence
    
    Keyword arguments:
    on_next: [Optional] Action to invoke for each element in the
            observable sequence.
    on_error: [Optional] Action to invoke upon exceptional
            termination of the observable sequence.
    on_completed: [Optional] Action to invoke upon graceful
            termination of the observable sequence.
    
    returns: Disposable object representing an observer's subscription
            to the observable sequence.
    """
    latch = config['concurrency'].Event()

    def onNext(src):
        if on_next:
            on_next(src)
    
    def onError(src):
        if on_error:
            on_error(src)
        latch.set()

    def onCompleted():
        if on_completed:
            on_completed()
        latch.set()

    disposable = source.subscribe(onNext, onError, onCompleted)
    latch.wait()

    return disposable