from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import TimeoutScheduler

class ObservableTime(object):
    def observable_timer_timespan_and_period(duetime, period, scheduler):
        if duetime == period:
            def subscribe(observer):
                def action(count):
                    observer.on_next(count);
                    count += 1
                    return count

                return scheduler.schedule_periodic(period, action, 0)
            return AnonymousObservable(subscribe)

        def deferred():
            return observable_timer_date_and_eriod(scheduler.now() + dueTime, period, scheduler)

        return Observable.defer(deferred)
    

    def interval(self, period, scheduler=None):
        scheduler = scheduler or TimeoutScheduler()
        return self.observable_timer_timespan_and_period(period, period, scheduler)

Observable.interval = ObservableTime.interval