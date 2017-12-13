from rx.core import Observer
from rx.core.notification import OnNext, OnError, OnCompleted

from .recorded import Recorded


class MockObserver(Observer):

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.messages = []

    def send(self, value):
        self.messages.append(Recorded(self.scheduler.clock, OnNext(value)))

    def throw(self, exception):
        self.messages.append(Recorded(self.scheduler.clock, OnError(exception)))

    def close(self):
        self.messages.append(Recorded(self.scheduler.clock, OnCompleted()))
