from rx.disposables import SingleAssignmentDisposable

class SchedulePeriodicRecursive(object):
    def __init__(self, scheduler, state, period, action):
        self._scheduler = scheduler
        self._state = state
        self._period = period
        self._action = action
    
    def tick(self, command, recurse):
        recurse(0, self._period)
        try:
            self._state = self._action(self._state)
        except Exception as exn:
            self._cancel.dispose()
            raise

    def start(self):
        d = SingleAssignmentDisposable()
        self._cancel = d
        d.disposable = self._scheduler.schedule_recursive_relative(self._period, tick.bind(self), 0)

        return d
