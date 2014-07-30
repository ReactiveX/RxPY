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
            self.dispose()

        def on_next(self, value):
            check_disposed(self)
            self.observer.on_next(value)

            def action(scheduler, state):
                log.debug('requested size', self.observable.window_size)
                self.observable.source.request(self.observable.window_size)

            self.received = (self.received+1) % self.observable.window_size
            if self.received == 0:
                self.scheduler.schedule(action)
                
        def dispose(self):
            self.observer = None
            if not self.cancel:
                self.cancel.dispose()
                self.cancel = None

            self.is_disposed = True

class WindowedObservable(Observable):
    def subscribe(self, observer):
        observer = WindowedObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        def action(scheduler, state):
            self.source.request(self.window_wize)

        self.scheduler.schedule(action)
        return self.subscription

    def __init__(self, source, window_size, scheduler):
        super(WindowedObservable, self).__init__(subscribe)

        self.source = source
        self.windowSize = window_size
        self.scheduler = scheduler
        self.is_disposed = False
