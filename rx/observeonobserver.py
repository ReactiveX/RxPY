from rx.scheduledobserver import ScheduledObserver


class ObserveOnObserver(ScheduledObserver):
    def __init__(self, scheduler, observer):
        super(ObserveOnObserver, self).__init__(scheduler, observer)

    def _next(self, value):
        super(ObserveOnObserver, self)._next(value)
        self.ensure_active()

    def _error(self, e):
        super(ObserveOnObserver, self)._error(e)
        self.ensure_active()

    def _completed(self):
        super(ObserveOnObserver, self)._completed()
        self.ensure_active()
