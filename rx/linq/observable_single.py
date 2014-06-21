from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.notification import OnNext, OnError, OnCompleted
from rx.subjects import Subject

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable, RefCountDisposable
from rx.concurrency import immediate_scheduler

from rx.internal import Enumerable, ArgumentOutOfRangeException
from rx.internal.utils import add_ref

def concat(sources):
    def subscribe(observer):
        e = iter(sources)
        is_disposed = False
        subscription = SerialDisposable()

        def action(action1, state=None):
            current = None
            
            if is_disposed:
                return
            try:
                current = next(e)
            except StopIteration:
                observer.on_completed()    
            except Exception as ex:
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe(
                    observer.on_next,
                    observer.on_error,
                    lambda: action1()
                )

        cancelable = immediate_scheduler.schedule_recursive(action)
        
        def dispose():
            nonlocal is_disposed
            is_disposed = True
        return CompositeDisposable(subscription, cancelable, Disposable(dispose))
    return AnonymousObservable(subscribe)

def catch_exception(sources):
    def subscribe(observer):
        e = iter(sources)
        is_disposed = False
        last_exception = None
        subscription = SerialDisposable()

        def action(action1, state=None):
            current = None
            
            def on_error(exn):
                nonlocal last_exception
                last_exception = exn
                action1()

            if is_disposed:
                return
            try:
                current = next(e)
            except StopIteration:
                if last_exception:
                    observer.on_error(last_exception)
                else:
                    observer.on_completed()    
            except Exception as ex:
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                
                d.disposable = current.subscribe(
                    observer.on_next,
                    on_error,
                    observer.on_completed
                )

        cancelable = immediate_scheduler.schedule_recursive(action)
        
        def dispose():
            nonlocal is_disposed
            is_disposed = True
        return CompositeDisposable(subscription, cancelable, Disposable(dispose))
    return AnonymousObservable(subscribe)


class ObservableSingle(Observable, metaclass=ObservableMeta):
    
    def __init__(self, subscribe):
        self.repeat = self.__repeat # Stitch in instance method

    # We do this to avoid overwriting the class method with the same name
    def __repeat(self, repeat_count=None):
        """Repeats the observable sequence a specified number of times. If the 
        repeat count is not specified, the sequence repeats indefinitely.
     
        1 - repeated = source.repeat()
        2 - repeated = source.repeat(42)
    
        Keyword arguments:
        repeat_count -- Number of times to repeat the sequence. If not 
            provided, repeats the sequence indefinitely.
    
        Returns the observable sequence producing the elements of the given 
        sequence repeatedly.   
        """

        return concat(Enumerable.repeat(self, repeat_count))

    def retry(self, retry_count=None):
        """Repeats the source observable sequence the specified number of times
        or until it successfully terminates. If the retry count is not 
        specified, it retries indefinitely.
     
        1 - retried = retry.repeat();
        2 - retried = retry.repeat(42);
    
        retry_count -- [Optional] Number of times to retry the sequence. If not
        provided, retry the sequence indefinitely.
        
        Returns an observable sequence producing the elements of the given 
        sequence repeatedly until it terminates successfully. 
        """
    
        return catch_exception(Enumerable.repeat(self, retry_count))

    def start_with(self, *args, **kw):
        """Prepends a sequence of values to an observable sequence with an 
        optional scheduler and an argument list of values to prepend.
        
        1 - source.start_with(1, 2, 3)
        2 - source.start_with(Scheduler.timeout, 1, 2, 3)
        
        Returns the source sequence prepended with the specified values.
        """
        
        scheduler = kw.get("scheduler")
        
        if not scheduler and isinstance(args[0], Scheduler):
            scheduler = args.pop(0)
        else:
            scheduler = immediate_scheduler

        sequence = [Observable.from_array(args, scheduler), self]
        return concat(Enumerable.for_each(sequence))

    def materialize(self):
        """Materializes the implicit notifications of an observable sequence as
        explicit notification values.
        
        Returns an observable sequence containing the materialized notification
        values from the source sequence.
        """
        source = self

        def subscribe(observer):
            def on_next(value):
                observer.on_next(OnNext(value))

            def on_error(exception):
                observer.on_next(OnError(exception))
                observer.on_completed()
            
            def on_completed():
                observer.on_next(OnCompleted())
                observer.on_completed()
            
            return source.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)
    
    def distinct_until_changed(self, key_selector, comparer):
        """Returns an observable sequence that contains only distinct 
        contiguous elements according to the key_selector and the comparer.
     
        1 - var obs = observable.distinct_until_changed();
        2 - var obs = observable.distinct_until_changed(function (x) { return x.id; });
        3 - var obs = observable.distinct_until_changed(function (x) { return x.id; }, function (x, y) { return x === y; });
     
        key_selector -- [Optional] A function to compute the comparison key for
            each element. If not provided, it projects the value.
        comparer -- [Optional] Equality comparer for computed key values. If 
            not provided, defaults to an equality comparer function.
    
        Return An observable sequence only containing the distinct contiguous 
        elements, based on a computed key value, from the source sequence.
        """
        source = self
        key_selector = key_selector or identity
        comparer = comparer or default_comparer
        
        def subscribe(observer):
            has_current_key = False
            current_key = None

            def on_next(value):
                comparer_equals = False
                try:
                    key = key_selector(value);
                except Exception as exception:
                    observer.onError(exception)
                    return
                
                if has_current_key:
                    try:
                        comparer_equals = comparer(currentKey, key);
                    except Exception as exception:
                        observer.onError(exception)
                        return
                    
                if not has_current_key or not comparer_equals:
                    has_current_key = True
                    current_key = key
                    observer.on_next(value)
            
            return source.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    def do_action(self, observer=None, on_next=None, on_error=None, on_completed=None):
        """Invokes an action for each element in the observable sequence and 
        invokes an action upon graceful or exceptional termination of the 
        observable sequence. This method can be used for debugging, logging, 
        etc. of query behavior by intercepting the message stream to run 
        arbitrary actions for messages on the pipeline.
    
        1 - observable.do_action(observer);
        2 - observable.do_action(on_next);
        3 - observable.do_action(on_next, on_error);
        4 - observable.do_action(on_next, on_error, on_eompleted);
     
        observer -- [Optional] Observer, or ... 
        on_next -- [Optional] Action to invoke for each element in the observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination 
            of the observable sequence. Used if only the observerOrOnNext parameter is also a function.
        on_completed -- [Optional] Action to invoke upon graceful termination 
            of the observable sequence. Used if only the observerOrOnNext parameter is also a function.
     
        Returns the source sequence with the side-effecting behavior applied.   
        """
        source = self
        if not observer is None:
            on_next = observer.on_next
            on_error = observer.on_error
            on_completed = observer.on_completed
        
        def subscribe(observer):
            def on_next(x):
                try:
                    on_next(x)
                except Exception as e:
                    observer.onError(e);
                
                observer.on_next(x)

            def on_error(exception):
                if not on_error:
                    observer.on_error(exception)
                else:
                    try:
                        on_error(exception)
                    except Exception as e:
                        observer.on_error(e)
                    
                    observer.on_error(exception)

            def on_completed():
                if not on_completed:
                    observer.on_completed()
                else:
                    try:
                        on_completed()
                    except Exception as e:
                        observer.on_error(e)
                    
                    observer.on_completed()
            return source.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)

    def window_with_count(self, count, skip=None):
        """Projects each element of an observable sequence into zero or more 
        windows which are produced based on element count information.
    
        1 - xs.window_with_count(10);
        2 - xs.window_with_count(10, 1);
    
        count -- Length of each window.
        skip -- [Optional] Number of elements to skip between creation of 
            consecutive windows. If not specified, defaults to the count.
        
        Returns an observable sequence of windows.
        """
        source = self
        if count <= 0:
            raise ArgumentOutOfRangeException()
        
        if skip is None:
            skip = count
        
        if skip <= 0:
            raise ArgumentOutOfRangeException()
        
        def subscribe(observer):
            m = SingleAssignmentDisposable()
            refCountDisposable = RefCountDisposable(m)
            n = 0
            q = []
                
            def create_window():
                nonlocal q
                
                s = Subject()
                q.append(s)
                observer.on_next(add_ref(s, refCountDisposable))
            
            create_window()
            
            def on_next(x):
                nonlocal q, n

                for item in q:
                    item.on_next(x)
                
                c = n - count + 1
                if c >= 0 and c % skip == 0:
                    s = q.pop(0);
                    s.on_completed()
                
                n += 1
                if (n % skip) == 0:
                    create_window()
                
            def on_error(exception):
                nonlocal q
                
                while len(q):
                    q.pop(0).on_error(exception)
                observer.on_error(exception)
            
            def on_completed():
                nonlocal q

                while len(q):
                    q.pop(0).on_completed()
                observer.on_completed()

            m.disposable = source.subscribe(on_next, on_error, on_completed)
            return refCountDisposable
        return AnonymousObservable(subscribe)
    
