from rx.internal import noop
from . import typing


class Disposable(typing.Disposable):  # pylint: disable=W0223
    """A static helper class for creating disposables."""

    @staticmethod
    def empty() -> typing.Disposable:
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(noop)

    @staticmethod
    def create(action) -> typing.Disposable:
        from rx.disposables import AnonymousDisposable
        return AnonymousDisposable(action)
