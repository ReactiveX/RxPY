from rx.core import bases
from rx.core.blockingobservable import BlockingObservable


def to_blocking(source: bases.Observable):
    return BlockingObservable(source)
