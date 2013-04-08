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
                print (current)
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
