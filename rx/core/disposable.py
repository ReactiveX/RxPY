from rx.internal import noop

from . import bases


class Disposable(bases.Disposable):
    @classmethod
    def empty(cls):
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(noop)

    @classmethod
    def create(cls, action):
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(action)
