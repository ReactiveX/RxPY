import logging

from rx import Observable
from rx.abstractobserver import AbstractObserver
from rx.concurrency import timeout_scheduler
from rx.disposables import CompositeDisposable
log = logging.getLogger('Rx')


class WindowedObserver(AbstractObserver):
    def __init__(self, observer, observable, cancel, scheduler):
        self.observer = observer
        self.observable = observable
        self.cancel = cancel
        self.scheduler = scheduler
        self.received = 0
        self.schedule_disposable = None

        super(WindowedObserver, self).__init__(self._next, self._error, self._completed)

    def _completed(self):
        self.observer.on_completed()
        self.dispose()

    def _error(self, error):
        self.observer.on_error(error)
        self.dispose()

    def _next(self, value):
        def inner_schedule_method(s, state):
            return self.observable.source.request(self.observable.window_size)

        self.observer.on_next(value)
        self.received = (self.received + 1) % self.observable.window_size
        if self.received == 0:
            self.schedule_disposable = self.scheduler.schedule(inner_schedule_method)

    def dispose(self):
        self.observer = None
        if self.cancel:
            self.cancel.dispose()
            self.cancel = None

        if self.schedule_disposable:
            self.schedule_disposable.dispose()
            self.schedule_disposable = None

        super(WindowedObserver, self).dispose()


class WindowedObservable(Observable):
    def __init__(self, source, window_size, scheduler=None):
        super(WindowedObservable, self).__init__(self._subscribe)

        self.source = source
        self.window_size = window_size
        self.scheduler = scheduler or timeout_scheduler
        self.subscription = None

    def _subscribe(self, observer):
        observer = WindowedObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        def action(scheduler, state):
            self.source.request(self.window_size)

        return CompositeDisposable(self.subscription, self.scheduler.schedule(action))
