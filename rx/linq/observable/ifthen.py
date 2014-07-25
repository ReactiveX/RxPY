from six import add_metaclass

from rx import Observable
from rx.internal import Enumerable, Enumerator
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableIfThen(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    @classmethod
    def if_then(cls, condition, then_source, else_source=None, scheduler=None):
        """Determines whether an observable collection contains values. 
        
        Example:
        1 - res = rx.Observable.if(condition, obs1)
        2 - res = rx.Observable.if(condition, obs1, obs2)
        3 - res = rx.Observable.if(condition, obs1, scheduler=scheduler)

        Keyword parameters:
        condition -- {Function} The condition which determines if the 
            then_source or else_source will be run.
        then_source -- {Observable} The observable sequence or Promise that 
            will be run if the condition function returns true.
        else_source -- {Observable} [Optional] The observable sequence or 
            Promise that will be run if the condition function returns False. 
            If this is not provided, it defaults to Rx.Observabe.Empty
        scheduler -- [Optional] Scheduler to use.
   
        Returns an observable {Observable} sequence which is either the 
        then_source or else_source."""
        
        else_source = else_source or Observable.empty(scheduler=scheduler)

        def factory():
            #isPromise(thenSource) && (thenSource = observableFromPromise(thenSource));
            #isPromise(elseSourceOrScheduler) && (elseSourceOrScheduler = observableFromPromise(elseSourceOrScheduler));
            
            return then_source if condition() else else_source
        return Observable.defer(factory)