from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler

@add_metaclass(ObservableMeta)
class ObservableAmb(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def __init__(self, subscribe):
        self.amb = self.__amb

    def __amb(self, right_source):
        """Propagates the observable sequence that reacts first.
    
        right_source Second observable sequence.
        
        returns an observable sequence that surfaces either of the given 
        sequences, whichever reacted first.
        """
        left_source = self

        def subscribe(observer):
            choice = [None]
            left_choice = 'L'
            right_choice = 'R',
            left_subscription = SingleAssignmentDisposable()
            right_subscription = SingleAssignmentDisposable()

            def choice_l():
                if not choice[0]:
                    choice[0] = left_choice
                    right_subscription.dispose()

            def choice_r():
                if not choice[0]:
                    choice[0] = right_choice
                    left_subscription.dispose()

            def on_left_next(left):
                choice_l()
                if choice[0] == left_choice:
                    observer.on_next(left)
            
            def on_left_error(err):
                choice_l()
                if choice[0] == left_choice:
                    observer.on_error(err)
                

            def on_left_completed():
                choice_l()
                if choice[0] == left_choice:
                    observer.on_completed()

            left_subscription.disposable = left_source.subscribe(on_left_next, on_left_error, on_left_completed)

            def on_right_next(right):
                choice_r()
                if choice[0] == right_choice:
                    observer.on_next(right)
            
            def on_right_error(err):
                choice_r()
                if choice[0] == right_choice:
                    observer.on_error(err)
            
            def on_right_completed():
                choice_r()
                if choice[0] == right_choice:
                    observer.on_completed()

            right_subscription.disposable = right_source.subscribe(on_right_next, on_right_error, on_right_completed)
            return CompositeDisposable(left_subscription, right_subscription)
        return AnonymousObservable(subscribe)

    @classmethod
    def amb(cls, *args):
        """Propagates the observable sequence that reacts first.
    
        E.g. winner = Rx.Observable.amb(xs, ys, zs)
     
        Returns an observable sequence that surfaces any of the given sequences, whichever reacted first.
        """
    
        acc = Observable.never()

        if isinstance(args[0], list):
            items = args[0]
        else:
            items = list(args)
        
        def func(previous, current):
            return previous.amb(current)
        
        for item in items:
            acc = func(acc, item)
        
        return acc
