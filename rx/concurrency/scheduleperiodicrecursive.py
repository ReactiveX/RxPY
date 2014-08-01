from rx.disposables import SingleAssignmentDisposable

class SchedulePeriodicRecursive(object):
    """Scheduler with support for running periodic tasks. This type of 
    scheduler can be used to run timers more efficiently instead of using 
    recursive scheduling."""

    def __init__(self, scheduler, period, action, state=None):
        """
        Keyword arguments:
        state -- Initial state passed to the action upon the first iteration.</param>
        period -- Period for running the work periodically.</param>
        action -- Action to be executed, potentially updating the state.</param>
        """
        self._scheduler = scheduler
        self._state = state
        self._period = period
        self._action = action
        self._cancel = None

    def tick(self, command, recurse):
        recurse(0, self._period)
        try:
            self._state = self._action(self._state)
        except Exception as exn:
            self._cancel.dispose()
            raise

    def start(self):
        """Returns the disposable object used to cancel the scheduled recurring
        action (best effort).
        """
        
        dis = SingleAssignmentDisposable()
        self._cancel = dis
        #dis.disposable = self._scheduler.schedule_recursive_relative(self._period, self.tick, 0)
        dis.disposable = self._scheduler.schedule_recursive_with_relative_and_state(self._period, self.tick, 0)

        return dis
