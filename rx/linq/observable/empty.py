from six import add_metaclass
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.concurrency import immediate_scheduler

@add_metaclass(ObservableMeta)
class ObservableEmpty(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def empty(cls, scheduler=None):
        """Returns an empty observable sequence, using the specified scheduler 
        to send out the single OnCompleted message.
     
        1 - res = rx.Observable.empty()
        2 - res = rx.Observable.empty(Rx.Scheduler.timeout)
    
        scheduler -- Scheduler to send the termination call on.
    
        returs an observable sequence with no elements.
        """

        scheduler = scheduler or immediate_scheduler
    
        def subscribe(observer):
            def action(scheduler, state):
                observer.on_completed()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

