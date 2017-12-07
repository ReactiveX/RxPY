from rx.core import Observer, Observable

from rx.internal.utils import check_disposed
from rx.concurrency import timeout_scheduler


class StopAndWaitObserver(Observer):

    def __init__(self, observer, observable, cancel, scheduler=None):
        super(StopAndWaitObserver, self).__init__()

        self.scheduler = scheduler
        self.observer = observer
        self.observable = observable
        self.cancel = cancel
        self.is_disposed = False

    def close(self):
        check_disposed(self)

        self.observer.close()
        self.dispose()

    def throw(self, error):
        check_disposed(self)

        self.observer.throw(error)
        self.dispose()

    def send(self, value):
        check_disposed(self)

        self.observer.send(value)

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

    def __init__(self, source, scheduler=None):
        super(StopAndWaitObservable, self).__init__()
        self.scheduler = scheduler or timeout_scheduler
        self.source = source
        self.subscription = None

    def _subscribe_core(self, observer, scheduler=None):
        observer = StopAndWaitObserver(observer, self, self.subscription, self.scheduler)
        self.subscription = self.source.subscribe(observer)

        def action(scheduler, state=None):
            self.source.request(1)

        self.scheduler.schedule(action)
        return self.subscription
