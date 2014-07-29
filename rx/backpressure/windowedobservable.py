import logging

from rx import Observer, Observable

log = logging.getLogger('Rx')

class WindowedObserver(Observer):
    def __init__(self, observer, observable, cancel, scheduler):
        self.observer = observer
        self.observable = observable
        self.cancel = cancel
        self.scheduler = scheduler
        self.received = 0
        self.is_disposed = False

        def on_completed(self):
            check_disposed(self)
            self.observer.on_completed()
            self.dispose()

        def on_error(self, error):
            check_disposed(self)
            self.observer.on_error(error)
            self.dispose();

        def on_next(value):
            check_disposed(self)
            self.observer.on_next(value)

            self.received = (self.received+1) % self.observable.window_size
            if self.received == 0:
                this = self
                this.scheduler.schedule(function () {
                log.debug('requested size', this.observable.window_size)
                this.observable.source.request(this.observable.window_size)

        def dispose(self):
            this.observer = None
            if not this.cancel:
              this.cancel.dispose()
              this.cancel = None

            this.is_disposed = True

class WindowedObservable(Observable):
    def subscribe(self, observer):
        observer = WindowedObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        this = self;

        def action(scheduler, state):
            this.source.request(this.window_wize);

        this.scheduler.schedule(action)
        return self.subscription

    def __init__(self, source, window_size, scheduler):
        super(WindowedObservable, self).__init__(subscribe)

        self.source = source
        self.windowSize = window_size
        self.scheduler = scheduler
        self.is_disposed = False
