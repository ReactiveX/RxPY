class InnerSubscription(object):
    def __init__(self, subject, observer):
        self.subject = subject
        self.observer = observer

    def dispose(self):
        if not self.subject.is_disposed and self.observer:
            if self.observer in self.subject.observers:
                self.subject.observers.remove(self.observer)
            self.observer = None

