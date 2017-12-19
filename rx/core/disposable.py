from rx.internal import noop

from . import typing


class Disposable(typing.Disposable):
    @classmethod
    def empty(cls) -> 'Disposable':
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(noop)

    @classmethod
    def create(cls, action) -> 'Disposable':
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(action)
