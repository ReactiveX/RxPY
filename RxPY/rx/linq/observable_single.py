from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler

from rx.internal import Enumerable

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
        self.repeat = self.__repeat

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

    def scan(self, seed=None, accumulator=None):
        """Applies an accumulator function over an observable sequence and 
        returns each intermediate result. The optional seed value is used as 
        the initial accumulator value. For aggregation behavior with no 
        intermediate results, see Observable.aggregate.
        
        1 - scanned = source.scan(lambda acc, x: acc + x)
        2 - scanned = source.scan(0, lambda acc, x: acc + x)
        
        Keyword arguments:
        seed -- [Optional] The initial accumulator value.
        accumulator -- An accumulator function to be invoked on each element.
        
        Returns an observable sequence containing the accumulated values.</returns>        
        """
        has_seed = False
        if not seed is None:
            has_seed = True

        source = self

        def defer():
            has_accumulation = False
            accumulation = None

            def projection(x):
                nonlocal accumulation, has_accumulation

                if has_accumulation:
                    accumulation = accumulator(accumulation, x)
                else:
                    accumulation =  accumulator(seed, x) if has_seed else x
                    has_accumulation = True
                
                return accumulation
            return source.select(projection)
        return Observable.defer(defer)

    def start_with(self, *args, **kw):
        """Prepends a sequence of values to an observable sequence with an 
        optional scheduler and an argument list of values to prepend.
        
        1 - source.start_with(1, 2, 3)
        2 - source.start_with(Rx.Scheduler.timeout, 1, 2, 3)
        
        Returns the source sequence prepended with the specified values.
        """
        
        scheduler = kw.get("scheduler")
        
        if not scheduler and isinstance(args[0], Scheduler):
            scheduler = args.pop(0)
        else:
            scheduler = immediate_scheduler

        sequence = [Observable.from_array(args, scheduler), self]
        return concat(Enumerable.for_each(sequence))
