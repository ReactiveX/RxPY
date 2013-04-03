from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, \
    SingleAssignmentDisposable
from rx.concurrency import TimeoutScheduler

class ObservableTime(Observable, metaclass=ObservableMeta):

    @classmethod
    def observable_timer_timespan_and_period(cls, duetime, period, scheduler):
        print ("ObservableTime:observable_timer_timespan_and_period()")
        
        if duetime == period:
            def subscribe(observer):
                def action(count):
                    observer.on_next(count)
                    count += 1
                    return count

                return scheduler.schedule_periodic(period, action, 0)
            return AnonymousObservable(subscribe)

        def deferred():
            return cls.observable_timer_date_and_period(scheduler.now() + duetime, period, scheduler)
        return Observable.defer(deferred)
    
    @classmethod
    def interval(cls, period, scheduler=None):
        print ("ObservableTime:interval(%s)" % period)
        scheduler = scheduler or TimeoutScheduler()
        return cls.observable_timer_timespan_and_period(period, period, scheduler)
