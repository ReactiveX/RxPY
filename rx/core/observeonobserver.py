from rx.core.scheduledobserver import ScheduledObserver


class ObserveOnObserver(ScheduledObserver):
    def __init__(self, scheduler, observer):
        super(ObserveOnObserver, self).__init__(scheduler, observer)

    def _send_core(self, value):
        super(ObserveOnObserver, self)._send_core(value)
        self.ensure_active()

    def _throw_core(self, e):
        super(ObserveOnObserver, self)._throw_core(e)
        self.ensure_active()

    def _close_core(self):
        super(ObserveOnObserver, self)._close_core()
        self.ensure_active()
