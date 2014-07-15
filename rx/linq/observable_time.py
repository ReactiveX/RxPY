import logging
from datetime import datetime, timedelta
from six import add_metaclass

from rx.internal.utils import add_ref
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.subjects import Subject
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable, RefCountDisposable
from rx.concurrency import timeout_scheduler

log = logging.getLogger("Rx")

# Rx Utils
class TimeInterval(object):
    def __init__(self, value, interval):
        self.value = value
        self.interval = interval

    #def __str__(self):
    #    return "%s@%s" % (self.value, self.interval)
    
    #def equals(other):
    #    return other.interval == self.interval and other.value == self.value


class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

    #def __str__(self):
    #    return "%s@%s" % (self.value, self.timestamp)
    
    #def equals(other):
    #    return other.timestamp == self.timestamp and other.value == self.value

@add_metaclass(ObservableMeta)
class ObservableTime(Observable):
    def window_with_time(self, timespan, timeshift=None, scheduler=None):
        source = self
        
        if timeshift is None:
            timeshift = timespan
        
        if not isinstance(timespan, timedelta):
            timespan = timedelta(milliseconds=timespan)
        if not isinstance(timeshift, timedelta):
            timeshift = timedelta(milliseconds=timeshift)

        scheduler = scheduler or timeout_scheduler
        
        def subscribe(observer):
            timer_d = SerialDisposable()
            next_shift = [timeshift]
            next_span = [timespan]
            total_time = [timedelta(0)]
            q = []
            
            group_disposable = CompositeDisposable(timer_d)
            ref_count_disposable = RefCountDisposable(group_disposable)
            
            def create_timer():
                m = SingleAssignmentDisposable()
                timer_d.disposable = m
                is_span = False
                is_shift = False

                if next_span[0] == next_shift[0]:
                    is_span = True
                    is_shift = True
                elif next_span[0] < next_shift[0]:
                    is_span = True
                else:
                    is_shift = True
                
                new_total_time = next_span[0] if is_span else next_shift[0]

                ts = new_total_time - total_time[0]
                total_time[0] = new_total_time
                if is_span:
                    next_span[0] += timeshift
                
                if is_shift:
                    next_shift[0] += timeshift
                
                def action(scheduler, state=None):
                    s = None
                    
                    if is_shift:
                        s = Subject()
                        q.append(s)
                        observer.on_next(add_ref(s, ref_count_disposable))
                    
                    if is_span:
                        s = q.pop(0)
                        s.on_completed()
                    
                    create_timer()
                m.disposable = scheduler.schedule_relative(ts, action)
            
            q.append(Subject())
            observer.on_next(add_ref(q[0], ref_count_disposable))
            create_timer()
            
            def on_next(x):
                for s in q:
                    s.on_next(x)
            
            def on_error(e):
                for s in q:
                    s.on_error(e)
                
                observer.on_error(e)
            
            def on_completed():
                for s in q:
                    s.on_completed()
                
                observer.on_completed()
            
            group_disposable.add(source.subscribe(on_next, on_error, on_completed))
            return ref_count_disposable
        return AnonymousObservable(subscribe)

    def window_with_time_or_count(self, timespan, count, scheduler=None):
        source = self
        scheduler = scheduler or timeout_scheduler

        def subscribe(observer):
            n = [0]
            s = [None]
            timer_d = SerialDisposable()
            window_id = [0]
            group_disposable = CompositeDisposable(timer_d)
            ref_count_disposable = RefCountDisposable(group_disposable)
            
            def create_timer(_id):
                m = SingleAssignmentDisposable()
                timer_d.disposable = m

                def action(scheduler, state):
                    if _id != window_id[0]:
                        return
                    
                    n[0] = 0
                    window_id[0] += 1
                    new_id = window_id[0]
                    s[0].on_completed()
                    s[0] = Subject()
                    observer.on_next(add_ref(s[0], ref_count_disposable))
                    create_timer(new_id)
        
                m.disposable = scheduler.schedule_relative(timespan, action)
            
            s[0] = Subject()
            observer.on_next(add_ref(s[0], ref_count_disposable))
            create_timer(0)
            
            def on_next(x):
                new_window = False
                new_id = 0
                
                s[0].on_next(x)
                n[0] += 1
                if n[0] == count:
                    new_window = True
                    n[0] = 0
                    window_id[0] += 1
                    new_id = window_id[0]
                    s[0].on_completed()
                    s[0] = Subject()
                    observer.on_next(add_ref(s[0], ref_count_disposable))
                
                if new_window:
                    create_timer(new_id)

            def on_error(e):
                s[0].on_error(e)
                observer.on_error(e)

            def on_completed():
                s[0].on_completed()
                observer.on_completed()
            
            group_disposable.add(source.subscribe(on_next, on_error, on_completed))
            return ref_count_disposable    
        return AnonymousObservable(subscribe)
    

    def buffer_with_time(self, timespan, timeshift=None, scheduler=None):
        """Projects each element of an observable sequence into zero or more 
        buffers which are produced based on timing information.
        
        1 - res = xs.buffer_with_time(1000) # non-overlapping segments of 1 second
        2 - res = xs.buffer_with_time(1000, 500) # segments of 1 second with time shift 0.5 seconds
        
        Keyword arguments:
        timespan -- Length of each buffer (specified as an integer denoting 
            milliseconds).
        timeshift -- [Optional] Interval between creation of consecutive 
            buffers (specified as an integer denoting milliseconds), or an 
            optional scheduler parameter. If not specified, the time shift 
            corresponds to the timespan parameter, resulting in non-overlapping
            adjacent buffers.
        scheduler -- [Optional] Scheduler to run buffer timers on. If not 
            specified, the timeout scheduler is used.
        
        Returns an observable sequence of buffers.
        """
        if not timeshift:
            timeshift = timespan
        
        scheduler = scheduler or timeout_scheduler
        
        return self.window_with_time(timespan, timeshift, scheduler) \
            .select_many(lambda x: x.to_array())
        

    def buffer_with_time_or_count(self, timespan, count, scheduler):
        """Projects each element of an observable sequence into a buffer that 
        is completed when either it's full or a given amount of time has 
        elapsed.
        
        1 - res = source.bufferWithTimeOrCount(5000, 50); # 5s or 50 items in an array
        2 - res = source.bufferWithTimeOrCount(5000, 50, Scheduler.timeout); # 5s or 50 items in an array
        
        Keyword arguments:
        timespan -- Maximum time length of a buffer.
        count -- Maximum element count of a buffer.
        scheduler -- [Optional] Scheduler to run bufferin timers on. If not 
            specified, the timeout scheduler is used.
        
        Returns an observable sequence of buffers.
        """
        scheduler = scheduler or timeout_scheduler
        return self.window_with_time_or_count(timespan, count, scheduler) \
            .select_many(lambda x: x.to_array())
    
    def time_interval(self, scheduler):
        """Records the time interval between consecutive values in an 
        observable sequence.
    
        1 - res = source.time_interval();
        2 - res = source.time_interval(Scheduler.timeout)
    
        Keyword arguments:
        scheduler -- [Optional] Scheduler used to compute time intervals. If 
            not specified, the timeout scheduler is used.
    
        Return An observable sequence with time interval information on values.
        """
        source = self
        scheduler = scheduler or timeout_scheduler

        def defer():
            last = [scheduler.now()]

            def selector(x):
                now = scheduler.now()
                span = now - last[0]
                last[0] = now
                return TimeInterval(value=x, interval=span)
                
            return source.select(selector)
        return Observable.defer(defer)

    def sample_observable(self, sampler):
        source = self

        def subscribe(observer):
            at_end = [None]
            has_value = [None]
            value = [None]

            def sample_subscribe(x):
                if has_value[0]:
                    has_value[0] = False
                    observer.on_next(value[0])
                
                if at_end[0]:
                    observer.on_completed()

            def on_next(new_value):
                has_value[0] = True
                value[0] = new_value
            
            def on_completed():
                at_end[0] = True

            return CompositeDisposable(
                source.subscribe(on_next, observer.on_error, on_completed),
                sampler.subscribe(sample_subscribe, observer.on_error, sample_subscribe)
            )
        return AnonymousObservable(subscribe)
    
    def sample(self, interval=None, sampler=None, scheduler=None):
        """Samples the observable sequence at each interval.
        
        1 - res = source.sample(sample_observable) # Sampler tick sequence
        2 - res = source.sample(5000) # 5 seconds
        2 - res = source.sample(5000, rx.scheduler.timeout) # 5 seconds
     
        Keyword arguments:
        source -- Source sequence to sample.
        interval -- Interval at which to sample (specified as an integer 
            denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the sampling timer on. If not
            specified, the timeout scheduler is used.
        
        Returns sampled observable sequence.
        """
        scheduler = scheduler or timeout_scheduler
        if not interval is None:
            return self.sample_observable(Observable.interval(interval, scheduler=scheduler))
        
        return self.sample_observable(sampler)

    def timeout(self, duetime, other=None, scheduler=None):
        """
        Returns the source observable sequence or the other observable sequence
        if duetime elapses.
    
        1 - res = source.timeout(new Date()); # As a date
        2 - res = source.timeout(5000); # 5 seconds
        3 - res = source.timeout(new Date(), rx.Observable.return_value(42)) # As a date and timeout observable
        4 - res = source.timeout(5000, rx.Observable.return_value(42)) # 5 seconds and timeout observable
        5 - res = source.timeout(new Date(), rx.Observable.return_value(42), rx.Scheduler.timeout) # As a date and timeout observable
        6 - res = source.timeout(5000, rx.Observable.return_value(42), rx.Scheduler.timeout) # 5 seconds and timeout observable
        
        duetime -- Absolute (specified as a datetime object) or relative time 
            (specified as an integer denoting milliseconds) when a timeout 
            occurs.
        other -- [Optional] Sequence to return in case of a timeout. If not 
            specified, a timeout error throwing sequence will be used.
        scheduler -- [Optional] Scheduler to run the timeout timers on. If not 
            specified, the timeout scheduler is used.
    
        Returns the source sequence switching to the other sequence in case of 
        a timeout.
        """
        
        scheduler_method = None
        source = self

        other = other or Observable.throw_exception(Exception("Timeout"))
        scheduler = scheduler or timeout_scheduler
        
        if isinstance(duetime, datetime):
            scheduler_method = scheduler.schedule_absolute
        else:
            duetime = duetime if isinstance(duetime, timedelta) else timedelta(milliseconds=duetime)
            scheduler_method = scheduler.schedule_relative
        
        def subscribe(observer):
            switched = [False]
            _id = [0]
            
            original = SingleAssignmentDisposable()
            subscription = SerialDisposable()
            timer = SerialDisposable()
            subscription.disposable = original

            def create_timer():
                my_id = _id[0]

                def action(scheduler, state=None):
                    switched[0] = (_id[0] == my_id)
                    timer_wins = switched[0]
                    if timer_wins:
                        subscription.disposable = other.subscribe(observer)
                    
                timer.disposable = scheduler_method(duetime, action)

            create_timer()
            def on_next(x):
                on_next_wins = not switched[0]
                if on_next_wins:
                    _id[0] += 1
                    observer.on_next(x)
                    create_timer()

            def on_error(e):
                on_error_wins = not switched[0]
                if on_error_wins:
                    _id[0] += 1
                    observer.on_error(e)

            def on_completed():
                on_completed_wins = not switched[0]
                if on_completed_wins:
                    _id[0] += 1
                    observer.on_completed()
            
            original.disposable = source.subscribe(on_next, on_error, on_completed)
            return CompositeDisposable(subscription, timer)
        return AnonymousObservable(subscribe)

    def timeout_with_selector(self, first_timeout=None, timeout_duration_selector=None, other=None):
        """Returns the source observable sequence, switching to the other 
        observable sequence if a timeout is signaled.
    
        1 - res = source.timeoutWithSelector(Rx.Observable.timer(500)); 
        2 - res = source.timeoutWithSelector(Rx.Observable.timer(500), function (x) { return Rx.Observable.timer(200); });
        3 - res = source.timeoutWithSelector(Rx.Observable.timer(500), function (x) { return Rx.Observable.timer(200); }, Rx.Observable.returnValue(42));
    
        [first_timeout]  Observable sequence that represents the timeout for the first element. If not provided, this defaults to Observable.never().
        [timeout_Duration_selector] Selector to retrieve an observable sequence that represents the timeout between the current element and the next element.
        [other]  Sequence to return in case of a timeout. If not provided, this is set to Observable.throwException(). 
        
        Returns the source sequence switching to the other sequence in case of 
        a timeout.
        """

        first_timeout = first_timeout or Observable.never()
        other = other or Observable.throw_exception(Exception('Timeout'))
        source = self
 

        def subscribe(observer):
            subscription = SerialDisposable()
            timer = SerialDisposable()
            original = SingleAssignmentDisposable()

            subscription.disposable = original

            switched = False
            _id = [0]
            
            def set_timer(timeout):
                my_id = _id[0]

                def timer_wins():
                    return _id[0] == my_id
                
                d = SingleAssignmentDisposable()
                timer.disposable = d
                
                def on_next(x):
                    if timer_wins():
                        subscription.disposable = other.subscribe(observer)
                    
                    d.dispose()
                
                def on_error(e):
                    if timer_wins():
                        observer.on_error(e)

                def on_completed():
                    if timer_wins():
                        subscription.disposable = other.subscribe(observer)
            
                d.disposable = timeout.subscribe(on_next, on_error, on_completed)

            set_timer(first_timeout)
            
            def observer_wins():
                res = not switched
                if res:
                    _id[0] += 1
                
                return res

            def on_next(x):
                if observer_wins():
                    observer.on_next(x)
                    timeout = None
                    try:
                        timeout = timeout_duration_selector(x)
                    except Exception as e:
                        observer.on_error(e)
                        return
                    
                    set_timer(timeout)
                
            def on_error(e):
                if observer_wins():
                    observer.on_error(e)
            
            def on_completed():
                if observer_wins():
                    observer.on_completed()

            original.disposable = source.subscribe(on_next, on_error, on_completed)
            return CompositeDisposable(subscription, timer)
        return AnonymousObservable(subscribe)

    @classmethod
    def generate_with_relative_time(cls, initial_state, condition, iterate, result_selector, time_selector, scheduler=None):
        """Generates an observable sequence by iterating a state from an 
        initial state until the condition fails.
        
        res = source.generate_with_relative_time(0, 
            lambda x: True, 
            lambda x: x + 1, 
            lambda x: x, 
            lambda x: 500
    
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning false).
        iterate -- Iteration step function.
        result_selector -- Selector function for results produced in the 
            sequence.
        time_selector -- Time selector function to control the speed of values 
            being produced each iteration, returning integer values denoting 
            milliseconds.
        scheduler -- [Optional] Scheduler on which to run the generator loop. 
            If not specified, the timeout scheduler is used.
    
        Returns the generated sequence.
        """
        scheduler = scheduler or timeout_scheduler
        
        def subscribe(observer):
            state = [initial_state]
            has_result = [False]
            result = [None]
            first = [True]
            time = None
            
            def action(this):
                if has_result[0]:
                    observer.on_next(result[0])
                
                try:
                    if first[0]:
                        first[0] = False
                    else:
                        state[0] = iterate(state[0])
                    
                    has_result[0] = condition(state[0])
                    if has_result[0]:
                        result[0] = result_selector(state[0])
                        time = time_selector(state[0])
                    
                except Exception as e:
                    observer.on_error(e)
                    return
                
                if has_result[0]:
                    this(time)
                else:
                    observer.on_completed()

            return scheduler.schedule_recursive_with_relative(0, action)
        return AnonymousObservable(subscribe)

    def delay_subscription(self, duetime, scheduler):
        """Time shifts the observable sequence by delaying the subscription.
    
        1 - res = source.delay_subscription(5000) # 5s
        2 - res = source.delay_subscription(5000, Scheduler.timeout) # 5 seconds
    
        duetime -- Absolute or relative time to perform the subscription at.
        scheduler [Optional] Scheduler to run the subscription delay timer on. 
            If not specified, the timeout scheduler is used.
    
        Returns time-shifted sequence.
        """
        scheduler = scheduler or timeout_scheduler

        def selector(_):
            return Observable.empty()
        return self.delay_with_selector(Observable.timer(duetime, scheduler), selector)

    def delay_with_selector(self, subscription_delay=None, delay_duration_selector=None):
        """Time shifts the observable sequence based on a subscription delay 
        and a delay selector function for each element.
    
        1 - res = source.delay_with_selector(lambda x: Scheduler.timer(5000)) # with selector only
        2 - res = source.delay_with_selector(Observable.timer(2000), lambda x: Observable.timer(x)) # with delay and selector
    
        subscription_delay -- [Optional] Sequence indicating the delay for the 
            subscription to the source. 
        delay_duration_selector [Optional] Selector function to retrieve a 
            sequence indicating the delay for each given element.
    
        Returns time-shifted sequence.
        """
        source = self
        sub_delay, selector = None, None

        if isinstance(subscription_delay, Observable):
            selector = delay_duration_selector
            sub_delay = subscription_delay
        else:
            selector = subscription_delay
        
        def subscribe(observer):
            delays = CompositeDisposable() 
            at_end = [False]

            def done():
                if (at_end[0] and delays.length == 0):
                    observer.on_completed()
            
            subscription = SerialDisposable()

            def start():
                def on_next(x):
                    try:
                        delay = selector(x)
                    except Exception as error:
                        observer.on_error(error)
                        return
                    
                    d = SingleAssignmentDisposable()
                    delays.add(d)

                    def on_next(_):
                        observer.on_next(x)
                        delays.remove(d)
                        done()
                    
                    def on_completed():
                        observer.on_next(x)
                        delays.remove(d)
                        done()
                    
                    d.disposable = delay.subscribe(on_next, observer.on_error, on_completed)
                
                def on_completed():
                    at_end[0] = True
                    subscription.dispose()
                    done()
                
                subscription.disposable = source.subscribe(on_next, observer.on_error, on_completed)

            if not sub_delay:
                start()
            else:
                subscription.disposable(sub_delay.subscribe(
                    lambda _: start(),
                    observer.on_error,
                    lambda: start()))
            
            return CompositeDisposable(subscription, delays)
        return AnonymousObservable(subscribe)
