from rx import Observer
from rx.notification import Notification, ON, OE, OC

from .recorded import Recorded

class MockObserver(Observer):

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.messages = []
    
    def on_next(self, value):
        self.messages.append(Recorded(self.scheduler.clock, ON(value)));
    
    def on_error(self, exception):
        self.messages.append(Recorded(self.scheduler.clock, OE(exception)));
    
    def on_completed(self):
        self.messages.append(Recorded(self.scheduler.clock, OC()))
