from rx.core import abc
from rx.core.blockingobservable import BlockingObservable


def to_blocking(source: abc.Observable):
    return BlockingObservable(source)
