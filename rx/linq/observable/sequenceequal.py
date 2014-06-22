from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, ScheduledDisposable, CompositeDisposable
from rx.internal import default_comparer

class ObservableSequenceEqual(Observable, metaclass=ObservableMeta):
    @staticmethod
    def sequence_equal_array(first, second, comparer):
        def subscribe(observer):
            count = 0
            length = len(second)
            
            def on_next(value):
                nonlocal count

                equal = False
                try:
                    if count < length:
                        equal = comparer(value, second[count])
                        count += 1
                    
                except Exception as ex:
                    observer.on_error(ex)
                    return
                
                if not equal:
                    observer.on_next(False)
                    observer.on_completed()

            def on_completed():
                observer.on_next(count == length)
                observer.on_completed()
            
            return first.subscribe(on_next, observer.on_error, on_completed)
        return AnonymousObservable(subscribe)
    
    def sequence_equal(self, second, comparer=None):
        """Determines whether two sequences are equal by comparing the 
        elements pairwise using a specified equality comparer.
        
        1 - res = source.sequence_equal([1,2,3]);
        2 - res = source.sequence_equal([{ value: 42 }], function (x, y) { return x.value === y.value; });
        3 - res = source.sequence_equal(Rx.Observable.returnValue(42));
        4 - res = source.sequence_equal(Rx.Observable.returnValue({ value: 42 }), function (x, y) { return x.value === y.value; });
    
        second -- Second observable sequence or array to compare.
        comparer -- [Optional] Comparer used to compare elements of both sequences.
     
        Returns an observable sequence that contains a single element which 
        indicates whether both sequences are of equal length and their 
        corresponding elements are equal according to the specified equality 
        comparer.
        """
    
        first = self
        comparer = comparer or default_comparer
        if isinstance(second, list):
            return ObservableAggregates.sequence_equal_array(first, second, comparer)
        
        def subscribe(observer):
            donel = False
            doner = False
            ql = []
            qr = []
            
            def on_next1(x):
                if len(qr) > 0:
                    v = qr.pop(0)
                    try:
                        equal = comparer(v, x)
                    except Exception as e:
                        observer.on_error(e)
                        return
                    
                    if not equal:
                        observer.on_next(False)
                        observer.on_completed()
                    
                elif doner:
                    observer.on_next(False)
                    observer.on_completed()
                else:
                    ql.append(x)

            def on_completed1():
                nonlocal donel

                donel = True
                if not len(ql):
                    if len(qr) > 0:
                        observer.on_next(False)
                        observer.on_completed()
                    elif doner:
                        observer.on_next(True)
                        observer.on_completed()

            def on_next2(x):
                if len(ql) > 0:
                    v = ql.pop(0)
                    try:
                        equal = comparer(v, x)
                    except Exception as exception:
                        observer.on_error(exception)
                        return
                    
                    if not equal:
                        observer.on_next(False)
                        observer.on_completed()
                    
                elif donel:
                    observer.on_next(False)
                    observer.on_completed()
                else:
                    qr.append(x)

            def on_completed2():
                nonlocal doner

                doner = True
                if not len(qr):
                    if len(ql) > 0:
                        observer.on_next(False)
                        observer.on_completed()
                    elif donel:
                        observer.on_next(True)
                        observer.on_completed()

            subscription1 = first.subscribe(on_next1, observer.on_error, on_completed1)
            subscription2 = second.subscribe(on_next2, observer.on_error, on_completed2)
            return CompositeDisposable(subscription1, subscription2)
        return AnonymousObservable(subscribe)