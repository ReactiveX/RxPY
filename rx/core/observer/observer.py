from typing import Any, Callable, Optional

from .. import typing
from rx.internal import noop, default_error


class Observer(typing.Observer, typing.Disposable):
    """Base class for implementations of the Observer class. This base
    class enforces the grammar of observers where OnError and
    OnCompleted are terminal messages.
    """

    def __init__(self,
                 on_next: Optional[typing.OnNext] = None,
                 on_error: Optional[typing.OnError] = None,
                 on_completed: Optional[typing.OnCompleted] = None
                 ) -> None:
        self.is_stopped = False
        self._handler_on_next = on_next or noop
        self._handler_on_error = on_error or default_error
        self._handler_on_completed = on_completed or noop

    def on_next(self, value: Any) -> None:
        """Notify the observer of a new element in the sequence."""
        if not self.is_stopped:
            self._on_next_core(value)

    def _on_next_core(self, value: Any) -> None:
        """For Subclassing purpose. This method is called by `on_next()`
        method until the observer is stopped.
        """
        self._handler_on_next(value)

    def on_error(self, error: Exception) -> None:
        """Notify the observer that an exception has occurred.

        Args:
            error: The error that occurred.
        """

        if not self.is_stopped:
            self.is_stopped = True
            self._on_error_core(error)

    def _on_error_core(self, error: Exception) -> None:
        """For Subclassing purpose. This method is called by `on_error()`
        method until the observer is stopped.
        """
        self._handler_on_error(error)

    def on_completed(self) -> None:
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            self.is_stopped = True
            self._on_completed_core()

    def _on_completed_core(self) -> None:
        """For Subclassing purpose. This method is called by `on_completed()`
        method until the observer is stopped.
        """
        self._handler_on_completed()

    def dispose(self) -> None:
        """Disposes the observer, causing it to transition to the
        stopped state."""
        self.is_stopped = True

    def fail(self, exn: Exception) -> bool:
        if not self.is_stopped:
            self.is_stopped = True
            self._on_error_core(exn)
            return True

        return False

    def throw(self, error: Exception) -> None:
        import traceback
        traceback.print_stack()
        if error:
            raise error
        1 / 0  # Raise division by zero

    def to_notifier(self) -> Callable:
        """Creates a notification callback from an observer.

        Returns the action that forwards its input notification to the
        underlying observer."""

        def func(notifier):
            return notifier.accept(self)
        return func

    def as_observer(self) -> 'Observer':
        """Hides the identity of an observer.

        Returns an observer that hides the identity of the specified
        observer.
        """
        return Observer(self.on_next, self.on_error, self.on_completed)
