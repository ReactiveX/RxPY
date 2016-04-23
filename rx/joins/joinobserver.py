from rx.observerbase import ObserverBase
from rx.disposables import SingleAssignmentDisposable


class JoinObserver(ObserverBase):

    def __init__(self, source, on_error):
        super(JoinObserver, self).__init__()

        self.source = source
        self.on_error = on_error
        self.queue = []
        self.active_plans = []
        self.subscription = SingleAssignmentDisposable()
        self.is_disposed = False

    def _next(self, notification):
        if not self.is_disposed:
            if notification.kind == 'E':
                self.on_error(notification.exception)
                return

            self.queue.append(notification)
            active_plans = self.active_plans[:]
            for plan in active_plans:
                plan.match()

    def _error(self, error):
        pass

    def _completed(self):
        pass

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
