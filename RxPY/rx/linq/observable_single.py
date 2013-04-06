from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import ImmediateScheduler

from rx.internal import Enumerable

class ObservableSingle(Observable, metaclass=ObservableMeta):
    
    def repeat(self, repeat_count=None):
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
        
        return Enumerable.repeat(repeat_count).concat()
