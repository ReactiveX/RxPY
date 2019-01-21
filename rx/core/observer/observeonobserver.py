from .scheduledobserver import ScheduledObserver


class ObserveOnObserver(ScheduledObserver):
    def _on_next_core(self, value):
        super()._on_next_core(value)
        self.ensure_active()

    def _on_error_core(self, error):
        super()._on_error_core(error)
        self.ensure_active()

    def _on_completed_core(self):
        super()._on_completed_core()
        self.ensure_active()
