from rx.disposables import SingleAssignmentDisposable

from .scheduler import Scheduler

class CatchScheduler(Scheduler):

    def local_now(self):
        return self._scheduler.now()

    def schedule_now(self, state, action):
        return self._scheduler.scheduleWithState(state, self._wrap(action))

    def schedule_relative(state, due_time, action):
        return self._scheduler.schedule_relative(due_time, self._wrap(action), state=state)

    def schedule_absolute(state, due_time, action):
        return self._scheduler.schedule_absolute(due_time, self._wrap(action), state=state)

    def __init__(self, scheduler, handler):
        self._scheduler = scheduler
        self._handler = handler
        self._recursive_original = None
        self._recursive_wrapper = None
        super(CatchScheduler, self).__init__(local_now, schedule_now, schedule_relative, schedule_absolute)

    def _clone(self, scheduler):
        return CatchScheduler(scheduler, self._handler)

    def _wrap(self, action):
        parent = self

        def wrapped_action(self, state):
            try:
                return action(parent._getRecursive_wrapper(self), state)
            except Exception as ex:
                if not parent._handler(ex):
                    raise Exception(ex)
                return Disposable.empty()
        return wrapped_action

    def _get_recursive_wrapper(self, scheduler):
        if self._recursive_original != scheduler:
            self._recursive_original = scheduler
            wrapper = self._clone(scheduler)
            wrapper._recursive_original = scheduler
            wrapper._recursive_wrapper = wrapper
            self._recursive_wrapper = wrapper

        return self._recursive_wrapper

    def schedule_periodic(self, period, action, state=None):
        d = SingleAssignmentDisposable()
        failed = False

        def action(state1):
            if failed:
                return None
            try:
                return action(state1)
            except Exception as ex:
                failed = True
                if not self._handler(e):
                    raise Exception(ex)
                d.dispose()
                return None

        d.disposable = self._scheduler.schedule_periodic(action, period, state)
        return d
