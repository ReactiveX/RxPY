from six import add_metaclass

from rx.internal import noop
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler
from rx.linq.enumerable import Enumerable

@add_metaclass(ObservableMeta)
class ObservableCombineLatest(Observable):
    def __init__(self, subscribe):
        self.on_error_resume_next = self.__on_error_resume_next

    def __on_error_resume_next(self, second):
        """Continues an observable sequence that is terminated normally or by 
        an exception with the next observable sequence.
    
        Keyword arguments:
        second -- Second observable sequence used to produce results after the first sequence terminates.
     
        Returns an observable sequence that concatenates the first and second sequence, even if the first sequence terminates exceptionally.
        """
    
        if not second:
            raise Exception('Second observable is required')
        
        return Observable.on_error_resume_next([self, second])

    @classmethod
    def on_error_resume_next(cls, *args):
        """Continues an observable sequence that is terminated normally or by 
        an exception with the next observable sequence.
     
        1 - res = Observable.on_error_resume_next(xs, ys, zs)
        2 - res = Observable.on_error_resume_next([xs, ys, zs])
    
        Returns an observable sequence that concatenates the source sequences, 
        even if a sequence terminates exceptionally.   
        """
    
        if args and isinstance(args[0], list):
            sources = args[0]
        else:
            sources = list(args)

        def subscribe(observer):
            subscription = SerialDisposable()
            pos = [0]
            
            def action(this, state=None):
                if pos[0] < len(sources):
                    current = sources[pos[0]]
                    pos[0] += 1
                    d = SingleAssignmentDisposable()
                    subscription.disposable = d
                    d.disposable = current.subscribe(observer.on_next, lambda ex: this(), lambda: this())
                else:
                    observer.on_completed()
                
            cancelable = immediate_scheduler.schedule_recursive(action)
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)
