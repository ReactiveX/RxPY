from abc import ABC, abstractmethod


class Scheduler(ABC):
    """Scheduler abstract base class. Untyped."""

    @property
    @abstractmethod
    def now(self):
        return NotImplemented

    @abstractmethod
    def schedule(self, action, state=None):
        return NotImplemented

    @abstractmethod
    def schedule_relative(self, duetime, action, state=None):
        return NotImplemented

    @abstractmethod
    def schedule_absolute(self, duetime, action, state=None):
        return NotImplemented

    @classmethod
    @abstractmethod
    def to_seconds(cls, value):
        return NotImplemented

    @classmethod
    @abstractmethod
    def to_datetime(cls, value):
        return NotImplemented

    @classmethod
    @abstractmethod
    def to_timedelta(cls, value):
        return NotImplemented
