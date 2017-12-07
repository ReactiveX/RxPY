from rx.core import ObserverBase
from rx.disposables import SingleAssignmentDisposable


class JoinObserver(ObserverBase):

    def __init__(self, source, throw):
        super(JoinObserver, self).__init__()

        self.source = source
        self.throw = throw
        self.queue = []
        self.active_plans = []
        self.subscription = SingleAssignmentDisposable()
        self.is_disposed = False

    def _send_core(self, notification):
        if not self.is_disposed:
            if notification.kind == 'E':
                self.throw(notification.exception)
                return

            self.queue.append(notification)
            active_plans = self.active_plans[:]
            for plan in active_plans:
                plan.match()

    def _throw_core(self, error):
        return NotImplemented

    def _close_core(self):
        return NotImplemented

    def add_active_plan(self, active_plan):
        self.active_plans.append(active_plan)

    def subscribe(self):
        self.subscription.disposable = self.source.materialize().subscribe(self)

    def remove_active_plan(self, active_plan):
        self.active_plans.remove(active_plan)
        if not len(self.active_plans):
            self.dispose()

    def dispose(self):
        super(JoinObserver, self).dispose()

        if not self.is_disposed:
            self.is_disposed = True
            self.subscription.dispose()
