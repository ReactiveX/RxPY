from typing import Any, Optional, TypeVar

from reactivex import abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)

from ..periodicscheduler import PeriodicScheduler

_TState = TypeVar("_TState")


class TkinterScheduler(PeriodicScheduler):
    """A scheduler that schedules work via the Tkinter main event loop.

    http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/universal.html
    http://effbot.org/tkinterbook/widget.htm"""

    def __init__(self, root: Any) -> None:
        """Create a new TkinterScheduler.

        Args:
            root: The Tk instance to use; typically, you would get this by
                import tkinter; tkinter.Tk()
        """

        super().__init__()
        self._root = root

    def schedule(
        self, action: typing.ScheduledAction[_TState], state: Optional[_TState] = None
    ) -> abc.DisposableBase:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        return self.schedule_relative(0.0, action, state)

    def schedule_relative(
        self,
        duetime: typing.RelativeTime,
        action: typing.ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        sad = SingleAssignmentDisposable()

        def invoke_action() -> None:
            sad.disposable = self.invoke_action(action, state=state)

        msecs = max(0, int(self.to_seconds(duetime) * 1000.0))
        timer = self._root.after(msecs, invoke_action)

        def dispose() -> None:
            self._root.after_cancel(timer)

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: typing.ScheduledAction[_TState],
        state: Optional[_TState] = None,
    ) -> abc.DisposableBase:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """

        duetime = self.to_datetime(duetime)
        return self.schedule_relative(duetime - self.now, action, state=state)
