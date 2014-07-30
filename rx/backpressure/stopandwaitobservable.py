from rx import Observer, Observable

class StopAndWaitObserver(Observer):

    def __init__(self, observer, observable, cancel, scheduler):
        super(StopAndWaitObserver, self).__init__()
        self.observer = observer
        self.observable = observable
        self.cancel = cancel
        self.is_disposed = False

    def on_completed(self):
        check_disposed(self)

        self.observer.on_completed()
        self.dispose()

    def on_error(self, error):
        check_disposed(self):

        self.observer.on_error(error)
        self.dispose()

    def on_next(value):
        check_disposed(self)

        self.observer.on_next(value)

        def action(scheduler, state):
            self.observable.source.request(1)
        self.scheduler.schedule(action)

    def dispose(self):
        self.observer = None
        if self.cancel:
            self.cancel.dispose()
            self.cancel = None

        self.is_disposed = True

class StopAndWaitObservable(Observable):

    def subscribe(observer):
        observer = StopAndWaitObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        def action(scheduler, state):
            self.source.request(1)

        self.scheduler.schedule(action)
        return self.subscription

    def __init__(self, source, scheduler):
        _super.call(self, subscribe)
        self.scheduler = scheduler
        self.source = source



