from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import pyboard_scheduler

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

class ObservableDelay:
    def observable_delay_timespan(self, duetime, scheduler):
        source = self
        
        def subscribe(observer):
            cancelable = SerialDisposable()
            exception = [None]
            active = [False]
            running = [False]
            queue = []

            def on_next(notification):
                should_run = False
                
                with self.lock:
                    if notification.value.kind == 'E':
                        del queue[:]
                        queue.append(notification)
                        exception[0] = notification.value.exception
                        should_run = not running[0]
                    else:
                        queue.append(Timestamp(value=notification.value, timestamp=notification.timestamp + duetime))
                        should_run = not active[0]
                        active[0] = True

                if should_run:
                    if exception[0]:
                        observer.on_error(exception[0])
                    else:
                        d = SingleAssignmentDisposable()
                        cancelable.disposable = d

                        def action(this):
                            if exception[0]:
                                return
                            
                            with self.lock:
                                running[0] = True
                                while True:
                                    result = None
                                    if len(queue) and queue[0].timestamp <= scheduler.now():
                                        result = queue.pop(0).value
    
                                    if result:
                                        result.accept(observer)
    
                                    if not result:
                                        break
    
                                should_recurse = False
                                recurse_duetime = 0
                                if len(queue) :
                                    should_recurse = True
                                    diff = queue[0].timestamp - scheduler.now()
                                    zero = 0
                                    recurse_duetime = max(zero, diff)
                                else:
                                    active[0] = False
    
                                ex = exception[0]
                                running[0] = False
                            
                            if ex:
                                observer.on_error(ex)
                            elif should_recurse:
                                this(recurse_duetime)

                        d.disposable = scheduler.schedule_recursive_with_relative(duetime, action)
            subscription = source.materialize().timestamp(scheduler).subscribe(on_next)
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)

    def observable_delay_date(self, duetime, scheduler):
        def defer():
            timespan = duetime - scheduler.now()
            return self.observable_delay_timespan(timespan, scheduler)

        return Observable.defer(defer)

    def delay(self, after=None, at=None, scheduler=None):
        """Time shifts the observable sequence by duetime. The relative time
        intervals between the values are preserved.

        1 - res = rx.Observable.delay(datetime())
        2 - res = rx.Observable.delay(datetime(), Scheduler.timeout)

        3 - res = rx.Observable.delay(5000)
        4 - res = rx.Observable.delay(5000, Scheduler.timeout)

        Keyword arguments:
        duetime -- Absolute (specified as a datetime object) or relative time
            (specified as an integer denoting milliseconds) by which to shift
            the observable sequence.
        scheduler -- [Optional] Scheduler to run the delay timers on. If not
            specified, the timeout scheduler is used.

        Returns time-shifted sequence."""

        scheduler = scheduler or pyboard_scheduler
        if at:
            observable = self.observable_delay_date(at, scheduler)
        else:
            observable = self.observable_delay_timespan(after, scheduler)

        return observable

Observable.delay = ObservableDelay.delay
Observable.observable_delay_date = ObservableDelay.observable_delay_date
Observable.observable_delay_timespan = ObservableDelay.observable_delay_timespan