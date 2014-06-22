from six import add_metaclass

from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.internal import SequenceContainsNoElementsError

@add_metaclass(ObservableMeta)
class ObservableToArray(Observable):
    def to_array(self):
        def accumulator(res, i):
            res.append(i)
            return res[:]
        
        return self.scan(accumulator, seed=[]).start_with([]).final_value()