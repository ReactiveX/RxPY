from typing import Any

from rx.internal import noop, default_error
from rx.disposable import SingleAssignmentDisposable

from ..typing import Observer


class AutoDetachObserver(Observer):

    def __init__(self, on_next=None, on_error=None, on_completed=None):
        self._on_next = on_next or noop
        self._on_error = on_error or default_error
        self._on_completed = on_completed or noop

        self._subscription = SingleAssignmentDisposable()
        self.is_stopped = False

    def on_next(self, value: Any) -> None:
        if self.is_stopped:
            return

        try:
            self._on_next(value)
        except Exception:
            self.dispose()
            raise

    def on_error(self, error) -> None:
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

    def set_disposable(self, value):
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
