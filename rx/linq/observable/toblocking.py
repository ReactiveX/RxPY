from rx import Observable
from rx.blockingobservable import BlockingObservable
from rx.internal import extensionmethod

@extensionmethod(Observable)
def to_blocking(self):
    return BlockingObservable(self)
