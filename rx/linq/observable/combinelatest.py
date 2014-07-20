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
        self.combine_latest = self.__combine_latest

    def __combine_latest(self, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever any of the observable
        sequences produces an element. This can be in the form of an argument 
        list of observables or an array.
     
        1 - obs = observable.combine_latest(obs1, obs2, obs3, function (o1, o2, o3) { return o1 + o2 + o3; })
        2 - obs = observable.combine_latest([obs1, obs2, obs3], function (o1, o2, o3) { return o1 + o2 + o3; })
     
        Returns an observable sequence containing the result of combining 
        elements of the sources using the specified result selector function.
        """
        
        args = list(args)
        if args and isinstance(args[0], list):
            args = args[0]

        args.insert(0, self)
        
        return Observable.combine_latest(*args)
    
    @classmethod
    def combine_latest(cls, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever any of the observable 
        sequences produces an element.
     
        1 - obs = Observable.combine_latest(obs1, obs2, obs3, function (o1, o2, o3) { return o1 + o2 + o3; })
        2 - obs = Observable.combine_latest([obs1, obs2, obs3], function (o1, o2, o3) { return o1 + o2 + o3; })     
     
        Returns an observable sequence containing the result of combining 
        elements of the sources using the specified result selector function.
        """
    
        if args and isinstance(args[0], list):
            args = args[0]
        else:
            args = list(args)
        
        result_selector = args.pop()
         
        def subscribe(observer):
            n = len(args)
            has_value = [False] * n
            has_value_all = [False]
            is_done = [False] * n
            values = [None] * n

            def next(i):
                has_value[i] = True
                
                if has_value_all[0] or all(has_value):
                    try:
                        res = result_selector(*values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    
                    observer.on_next(res)
                elif all([x for j, x in enumerate(is_done) if j != i]):
                    observer.on_completed()

                has_value_all[0] = all(has_value)

            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()
             
            subscriptions = [None] * n
            def func(i):
                subscriptions[i] = SingleAssignmentDisposable()
                
                def on_next(x):
                    values[i] = x
                    next(i)
                
                def on_completed():
                    done(i)
                
                subscriptions[i].disposable = args[i].subscribe(on_next, observer.on_error, on_completed)

            for idx in range(n):
                func(idx)
            return CompositeDisposable(subscriptions)
        return AnonymousObservable(subscribe)


    def concat_all(self):
        """Concatenates an observable sequence of observable sequences.
        
        Returns an observable sequence that contains the elements of each 
        observed inner sequence, in sequential order.
        """
        return self.merge(1)

    def skip_until(self, other):
        """Returns the values from the source observable sequence only after 
        the other observable sequence produces a value.
     
        other -- The observable sequence that triggers propagation of elements of the source sequence.
     
        Returns an observable sequence containing the elements of the source 
        sequence starting from the point the other sequence triggered 
        propagation.    
        """
    
        source = self

        def subscribe(observer):
            is_open = [False]

            def on_next(left):
                if is_open[0]:
                    observer.on_next(left)
            
            def on_completed():
                if is_open[0]:
                    observer.on_completed()
            
            disposables = CompositeDisposable(source.subscribe(on_next, observer.on_error, on_completed))

            right_subscription = SingleAssignmentDisposable()
            disposables.add(right_subscription)

            def on_next2(x):
                is_open[0] = True
                right_subscription.dispose()
            
            def on_completed2():
                right_subscription.dispose()

            right_subscription.disposable = other.subscribe(on_next2, observer.on_error, on_completed2)

            return disposables
        return AnonymousObservable(subscribe)

    def take_until(self, other):
        """Returns the values from the source observable sequence until the 
        other observable sequence produces a value.

        Keyword arguments:    
        other -- Observable sequence that terminates propagation of elements of 
            the source sequence.
    
        Returns an observable sequence containing the elements of the source 
        sequence up to the point the other sequence interrupted further propagation.
        """
        source = self

        def subscribe(observer):
            def on_completed(x):
                observer.on_completed()

            return CompositeDisposable(
                source.subscribe(observer),
                other.subscribe(on_completed, observer.on_error, noop)
            )
        return AnonymousObservable(subscribe)

    def zip_array(self, second, result_selector):
        first = self

        def subscribe(observer):
            length = len(second)
            index = [0]
            
            def on_next(left):
                if index[0] < length:
                    right = second[index[0]]
                    index[0] += 1
                    try:
                        result = result_selector(left, right)
                    except Exception as e:
                        observer.on_error(e)
                        return
                    
                    observer.on_next(result)
                else:
                    observer.on_completed()
                
            return first.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    def zip(self, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever all of the observable 
        sequences or an array have produced an element at a corresponding index.
        
        The last element in the arguments must be a function to invoke for each 
        series of elements at corresponding indexes in the sources.
        
        1 - res = obs1.zip(obs2, fn)
        2 - res = x1.zip([1,2,3], fn)  
     
        Returns an observable sequence containing the result of combining 
        elements of the sources using the specified result selector function. 
        """

        if args and isinstance(args[0], list):
            return self.zip_array(list(args))
        
        parent = self
        sources = list(args)
        result_selector = sources.pop()
        sources.insert(0, parent)
        
        def subscribe(observer):
            n = len(sources)
            queues = [[] for _ in range(n)]
            is_done = [False] * n
            
            def next(i):
                if all([len(q) for q in queues]):
                    try:
                        queued_values = [x.pop(0) for x in queues]
                        res = result_selector(*queued_values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    
                    observer.on_next(res)
                elif all([x for j, x in enumerate(is_done) if j != i]):
                    observer.on_completed()
                
            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()

            subscriptions = [None]*n

            def func(i):
                subscriptions[i] = SingleAssignmentDisposable()

                def on_next(x):
                    queues[i].append(x)
                    next(i)
                
                subscriptions[i].disposable = sources[i].subscribe(on_next, observer.on_error, lambda: done(i))
                
            for idx in range(n):
                func(idx)
            return CompositeDisposable(subscriptions)
        return AnonymousObservable(subscribe)
