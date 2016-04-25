from rx.core import ObservableBase


class AnonymousStream(ObservableBase):
    def __init__(self, observer, observable):
        super(AnonymousStream, self).__init__()

        self.observer = observer
        self.observable = observable

    def _subscribe_core(self, observer):
        return self.observable.subscribe(observer)

    def on_completed(self):
        self.observer.on_completed()

    def on_error(self, exception):
        self.observer.on_error(exception)

    def on_next(self, value):
        self.observer.on_next(value)

AnonymousStream = AnonymousStream
