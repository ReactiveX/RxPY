from abc import ABC, abstractmethod


class PeriodicScheduler(ABC):
    """PeriodicScheduler abstract base class. Untyped."""

    @abstractmethod
    def schedule_periodic(self, period, action, state=None):
        return NotImplemented
