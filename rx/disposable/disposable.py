from typing import Optional
from threading import RLock

from rx.internal import noop
from rx.core import typing


class Disposable(typing.Disposable):
    """Main disposable class"""

    def __init__(self, action: Optional[typing.Action] = None) -> None:
        """Creates a disposable object that invokes the specified
        action when disposed.

        Args:
            action: Action to run during the first call to dispose.
                The action is guaranteed to be run at most once.

        Returns:
            The disposable object that runs the given action upon
            disposal.
        """

        self.is_disposed = False
        self.action = action or noop

        self.lock = RLock()

        super().__init__()

    def dispose(self) -> None:
        """Performs the task of cleaning up resources."""

        dispose = False
        with self.lock:
            if not self.is_disposed:
                dispose = True
                self.is_disposed = True

        if dispose:
            self.action()
