from rx.core.scheduledobserver import ScheduledObserver


class ObserveOnObserver(ScheduledObserver):
    def _send_core(self, value):
        super()._send_core(value)
        self.ensure_active()

    def _throw_core(self, error):
        super()._throw_core(error)
        self.ensure_active()

    def _close_core(self):
        super()._close_core()
        self.ensure_active()
