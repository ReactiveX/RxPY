from rx.core import Observable
from rx.core.blockingobservable import BlockingObservable


def to_blocking(source: Observable):
    return BlockingObservable(source)
