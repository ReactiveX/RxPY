from typing import TypeVar

from .scheduledobserver import ScheduledObserver

_T = TypeVar("_T")


class ObserveOnObserver(ScheduledObserver[_T]):
    def _on_next_core(self, value: _T) -> None:
        super()._on_next_core(value)
        self.ensure_active()

    def _on_error_core(self, error: Exception) -> None:
        super()._on_error_core(error)
        self.ensure_active()

    def _on_completed_core(self) -> None:
        super()._on_completed_core()
        self.ensure_active()
