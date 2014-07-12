from six import add_metaclass
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable
from rx.concurrency import immediate_scheduler, current_thread_scheduler

@add_metaclass(ObservableMeta)
class ObservableCreation(Observable):

    @classmethod
    def create(cls, subscribe):
        def _subscribe(observer):
            return Disposable(subscribe(observer))
        
        return AnonymousObservable(_subscribe)

    @classmethod
    def create_with_disposable(cls, subscribe):
        return AnonymousObservable(subscribe)

    @classmethod
    def from_array(cls, array, scheduler=None):
        """Converts an array to an observable sequence, using an optional 
        scheduler to enumerate the array.
    
        1 - res = rx.Observable.from_array([1,2,3])
        2 - res = rx.Observable.from_array([1,2,3], rx.Scheduler.timeout)
     
        Keyword arguments:
        scheduler -- [Optional] Scheduler to run the enumeration of the input
            sequence on.
     
        Returns the observable sequence whose elements are pulled from the 
        given enumerable sequence.
        """

        scheduler = scheduler or current_thread_scheduler

        def subscribe(observer):
            count = [0]
            
            def action(action1, state=None):
                if count[0] < len(array):
                    observer.on_next(array[count[0]])
                    count[0] += 1
                    action1(action)
                else:
                    observer.on_completed()
                
            return scheduler.schedule_recursive(action)
        return AnonymousObservable(subscribe)

    @classmethod
    def return_value(cls, value, scheduler=None):
        scheduler = scheduler or immediate_scheduler

        def subscribe(observer):
            def action(scheduler, state=None):
                observer.on_next(value)
                observer.on_completed()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    @classmethod
    def throw_exception(cls, exception, scheduler=None):
        """Returns an observable sequence that terminates with an exception, 
        using the specified scheduler to send out the single OnError message.
    
        1 - res = rx.Observable.throw_exception(new Error('Error'));
        2 - res = rx.Observable.throw_exception(new Error('Error'), Rx.Scheduler.timeout);
     
        Keyword arguments:
        exception -- An object used for the sequence's termination.
        scheduler -- Scheduler to send the exceptional termination call on. If
            not specified, defaults to ImmediateScheduler.
    
        Returns the observable sequence that terminates exceptionally with the 
        specified exception object.
        """
        scheduler = scheduler or immediate_scheduler
        
        exception = Exception(exception) if type(exception) is Exception else exception

        def subscribe(observer):
            def action(scheduler, state):
                observer.on_error(exception)

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    @classmethod
    def using(cls, resource_factory, observable_factory):
        """Constructs an observable sequence that depends on a resource object,
        whose lifetime is tied to the resulting observable sequence's lifetime.
      
        1 - res = Rx.Observable.using(function () { return new AsyncSubject(); }, function (s) { return s; });
    
        Keyword arguments:
        resource_factory -- Factory function to obtain a resource object.
        observable_factory -- Factory function to obtain an observable sequence
            that depends on the obtained resource.
     
        Returns an observable sequence whose lifetime controls the lifetime of 
        the dependent resource object.
        """
        def subscribe(observer):
            disposable = Disposable.empty()
            try:
                resource = resource_factory()
                if resource:
                    disposable = resource
                
                source = observable_factory(resource)
            except Exception as exception:
                d = Observable.throw_exception(exception).subscribe(observer)
                return CompositeDisposable(d, disposable)
            
            return CompositeDisposable(source.subscribe(observer), disposable)
        return AnonymousObservable(subscribe)
