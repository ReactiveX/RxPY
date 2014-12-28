import logging

from rx import Observable
from rx.abstractobserver import AbstractObserver
from rx.concurrency import timeout_scheduler

log = logging.getLogger('Rx')


class WindowedObserver(AbstractObserver):
    def __init__(self, observer, observable, cancel, scheduler):
        self.observer = observer
        self.observable = observable
        self.cancel = cancel
        self.scheduler = scheduler
        self.received = 0
        self.is_disposed = False

        def on_completed(self):
            self.observer.on_completed()
            self.dispose()

        def on_error(self, error):
            self.observer.on_error(error)
            self.dispose()

        def on_next(self, value):
            self.observer.on_next(value)

            def action(scheduler, state):
                log.debug('requested size: %s', self.observable.window_size)
                self.observable.source.request(self.observable.window_size)

            self.received = (self.received+1) % self.observable.window_size
            if self.received == 0:
                self.scheduler.schedule(action)

        def dispose(self):
            self.observer = None
            if not self.cancel:
                self.cancel.dispose()
                self.cancel = None

            super(AbstractObserver, self).dispose()


class WindowedObservable(Observable):
    def __init__(self, source, window_size, scheduler=None):
        super(WindowedObservable, self).__init__(self._subscribe)

        self.source = source
        self.window_size = window_size
        self.scheduler = scheduler or timeout_scheduler

    def _subscribe(self, observer):
        observer = WindowedObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        def action(scheduler, state):
            self.source.request(self.window_size)

        self.scheduler.schedule(action)
        return self.subscription

