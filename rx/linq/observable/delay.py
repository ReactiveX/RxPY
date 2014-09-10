import logging
from datetime import datetime, timedelta
from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

log = logging.getLogger("Rx")

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

@add_metaclass(ExtensionMethod)
class ObservableDelay(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def observable_delay_timespan(self, duetime, scheduler):
        source = self
        
        def subscribe(observer):
            cancelable = SerialDisposable()
            exception = [None]
            active = [False]
            running = [False]
            q = []

            def on_next(notification):
                log.debug("observable_delay_timespan:subscribe:on_next()")
                should_run = False
                d = None

                if notification.value.kind == 'E':
                    del q[:]
                    q.append(notification)
                    exception[0] = notification.value.exception
                    should_run = not running[0]
                else:
                    q.append(Timestamp(value=notification.value, timestamp=notification.timestamp + duetime))
                    should_run = not active[0]
                    active[0] = True
                
                if should_run:
                    if exception[0]:
                        log.error("*** Exception: %s", exception[0])
                        observer.on_error(exception[0])
                    else:
                        d = SingleAssignmentDisposable()
                        cancelable.disposable = d

                        def action(self):
                            if exception[0]:
                                log.error("observable_delay_timespan:subscribe:on_next:action(), exception: %s", exception[0])
                                return
                            
                            running[0] = True
                            while True:
                                result = None
                                if len(q) and q[0].timestamp <= scheduler.now():
                                    result = q.pop(0).value
                                
                                if result:
                                    result.accept(observer)
                                
                                if not result:
                                    break
                            
                            should_recurse = False
                            recurse_duetime = 0
                            if len(q) > 0:
                                should_recurse = True
                                diff = q[0].timestamp - scheduler.now()
                                zero = timedelta(0) if isinstance(diff, timedelta) else 0
                                recurse_duetime = max(zero, diff)
                            else:
                                active[0] = False
                            
                            e = exception[0]
                            running[0] = False
                            if e:
                                observer.on_error(e)
                            elif should_recurse:
                                self(recurse_duetime)

                        d.disposable = scheduler.schedule_recursive_with_relative(duetime, action)
            subscription = source.materialize().timestamp(scheduler).subscribe(on_next)
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)

    def observable_delay_date(self, duetime, scheduler):
        def defer():
            timespan = duetime - scheduler.now()
            return self.observable_delay_timespan(timespan, scheduler)
        
        return Observable.defer(defer)

    def delay(self, duetime, scheduler=None):
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
        
        Returns time-shifted sequence.
        """
        scheduler = scheduler or timeout_scheduler
        if isinstance(duetime, datetime):
            observable = self.observable_delay_date(duetime, scheduler)
        else:
            duetime = duetime if isinstance(duetime, timedelta) else timedelta(milliseconds=duetime)
            observable = self.observable_delay_timespan(duetime, scheduler)

        return observable
