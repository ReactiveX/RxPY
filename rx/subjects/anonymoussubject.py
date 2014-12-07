from rx import Observable


class AnonymousSubject(Observable):
    def __init__(self, observer, observable):
        super(AnonymousSubject, self).__init__(self._subscribe)
        
        self.observer = observer
        self.observable = observable

    def _subscribe(self, observer):
        return self.observable.subscribe(observer)

    def on_completed(self):
        self.observer.on_completed()

    def on_error(self, exception):
        self.observer.on_error(exception)

    def on_next(self, value):
        self.observer.on_next(value)
