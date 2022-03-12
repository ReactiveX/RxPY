from typing import Optional, TypeVar

from reactivex.disposable import SingleAssignmentDisposable
from reactivex.internal import default_error, noop

from .. import abc, typing

_T_in = TypeVar("_T_in", contravariant=True)


class AutoDetachObserver(abc.ObserverBase[_T_in]):
    def __init__(
        self,
        on_next: Optional[typing.OnNext[_T_in]] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
    ) -> None:
        self._on_next = on_next or noop
        self._on_error = on_error or default_error
        self._on_completed = on_completed or noop

        self._subscription = SingleAssignmentDisposable()
        self.is_stopped = False

    def on_next(self, value: _T_in) -> None:
        if self.is_stopped:
            return
        self._on_next(value)

    def on_error(self, error: Exception) -> None:
        if self.is_stopped:
            return
        self.is_stopped = True

        try:
            self._on_error(error)
        finally:
            self.dispose()

    def on_completed(self) -> None:
        if self.is_stopped:
            return
        self.is_stopped = True

        try:
            self._on_completed()
        finally:
            self.dispose()

    def set_disposable(self, value: abc.DisposableBase) -> None:
        self._subscription.disposable = value

    subscription = property(fset=set_disposable)

    def dispose(self) -> None:
        self.is_stopped = True
        self._subscription.dispose()

    def fail(self, exn: Exception) -> bool:
        if self.is_stopped:
            return False

        self.is_stopped = True
        self._on_error(exn)
        return True
