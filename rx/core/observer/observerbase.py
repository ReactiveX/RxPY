from typing import Callable, Any
from abc import abstractmethod

from ..typing import Observer, Disposable


class ObserverBase(Observer, Disposable):
    """Base class for implementations of the Observer class. This base
    class enforces the grammar of observers where OnError and
    OnCompleted are terminal messages.
    """

    def __init__(self):
        self.is_stopped = False

    def on_next(self, value: Any) -> None:
        """Notify the observer of a new element in the sequence."""
        if not self.is_stopped:
            self._on_next_core(value)

    @abstractmethod
    def _on_next_core(self, value: Any) -> None:
        return NotImplemented

    def on_error(self, error: Exception) -> None:
        """Notify the observer that an exception has occurred.

        Args:
            error: The error that occurred.
        """

        if not self.is_stopped:
            self.is_stopped = True
            self._on_error_core(error)

    @abstractmethod
    def _on_error_core(self, error: Exception) -> None:
        return NotImplemented

    def on_completed(self) -> None:
        """Notifies the observer of the end of the sequence."""

        if not self.is_stopped:
            self.is_stopped = True
            self._on_completed_core()

    @abstractmethod
    def _on_completed_core(self) -> None:
        return NotImplemented

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

    def to_notifier(self) -> Callable:
        """Creates a notification callback from an observer.

        Returns the action that forwards its input notification to the
        underlying observer."""

        def func(notifier):
            return notifier.accept(self)
        return func

    def as_observer(self) -> 'ObserverBase':
        """Hides the identity of an observer.

        Returns an observer that hides the identity of the specified
        observer.
        """
        from .anonymousobserver import AnonymousObserver
        return AnonymousObserver(self.on_next, self.on_error, self.on_completed)

