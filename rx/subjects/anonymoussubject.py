from rx.core import Observable


class AnonymousSubject(Observable):
    def __init__(self, observer, observable):
        super(AnonymousSubject, self).__init__()

        self.observer = observer
        self.observable = observable

    def _subscribe_core(self, observer, scheduler=None):
        return self.observable.subscribe(observer)

    def close(self):
        self.observer.close()

    def throw(self, exception):
        self.observer.throw(exception)

    def send(self, value):
        self.observer.send(value)
