
from rx.internal import Enumerable, noop
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler

from .observable_single import concat, catch_exception

class ObservableMultiple(Observable, metaclass=ObservableMeta):
    def __init__(self, subscribe):
        self.concat = self.__concat # Stitch in instance method
        self.merge = self.__merge
        self.amb = self.__amb
        self.catch_exception = self.__catch_exception
        self.on_error_resume_next = self.__on_error_resume_next
        self.combine_latest = self.__combine_latest

    def __amb(self, right_source):
        """Propagates the observable sequence that reacts first.
    
        right_source Second observable sequence.
        
        returns an observable sequence that surfaces either of the given 
        sequences, whichever reacted first.
        """
        left_source = self

        def subscribe(observer):
            choice = None
            left_choice = 'L'
            right_choice = 'R',
            left_subscription = SingleAssignmentDisposable()
            right_subscription = SingleAssignmentDisposable()

            def choiceL():
                nonlocal choice

                if not choice:
                    choice = left_choice
                    right_subscription.dispose()

            def choiceR():
                nonlocal choice

                if not choice:
                    choice = right_choice
                    left_subscription.dispose()

            def on_left_next(left):
                choiceL()
                if choice == left_choice:
                    observer.on_next(left)
            
            def on_left_error(err):
                choiceL()
                if choice == left_choice:
                    observer.on_error(err)
                

            def on_left_completed():
                choiceL()
                if choice == left_choice:
                    observer.on_completed()

            left_subscription.disposable = left_source.subscribe(on_left_next, on_left_error, on_left_completed)

            def on_right_next(right):
                choiceR()
                if choice == right_choice:
                    observer.on_next(right)
            
            def on_right_error(err):
                choiceR()
                if choice == right_choice:
                    observer.on_error(err)
            
            def on_right_completed():
                choiceR()
                if choice == right_choice:
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

    @staticmethod
    def catch_handler(source, handler):
        def subscribe(observer):
            d1 = SingleAssignmentDisposable()
            subscription = SerialDisposable()

            subscription.disposable = d1
            
            def on_error(exception):
                try:
                    result = handler(exception)
                except Exception as ex:
                    observer.on_error(ex)
                    return
                
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = result.subscribe(observer)
            
            d1.disposable = source.subscribe(observer.on_next, on_error, observer.on_completed)
            return subscription
        return AnonymousObservable(subscribe)
    

    def __catch_exception(self, second=None, handler=None):
        """Continues an observable sequence that is terminated by an exception 
        with the next observable sequence.
     
        1 - xs.catch_exception(ys)
        2 - xs.catch_exception(lambda ex: ys(ex))
    
        Keyword arguments:
        handler -- Exception handler function that returns an observable sequence 
            given the error that occurred in the first sequence.
        second -- Second observable sequence used to produce results when an 
            error occurred in the first sequence.
    
        Returns an observable sequence containing the first sequence's 
        elements, followed by the elements of the handler sequence in case an 
        exception occurred.
        """
    
        if handler or not isinstance(second, Observable):
            return self.catch_handler(self, handler or second)
        
        return Observable.catch_exception([self, second])

    @classmethod
    def catch_exception(cls, *args):
        """Continues an observable sequence that is terminated by an 
        exception with the next observable sequence.
     
        1 - res = Observable.catch_exception(xs, ys, zs)
        2 - res = Observable.catch_exception([xs, ys, zs])
    
        Returns an observable sequence containing elements from consecutive 
        source sequences until a source sequence terminates successfully.
        """

        if args and isinstance(args[0], list):
            items = args[0]
        else:
            items = list(args)

        return catch_exception(Enumerable.for_each(items))

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
            args[0].insert(0, self)
        else:
            args.insert(0, self)
        
        return Observable.combine_latest(args)
    
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
    
        args = list(args)
        
        result_selector = args.pop(0)
        
        if args and isinstance(args[0], list):
            args = args[0]
            
        def subscribe(observer):
            n = len(args)
            has_value = [False] * n
            has_value_all = False
            is_done = [False] * n
            values = []

            def next(i):
                nonlocal has_value_all

                has_value[i] = True
                if has_value_all or all(has_value):
                    try:
                        res = result_selector(values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    
                    observer.on_next(res)
                elif all([j != i for i, j in enumerate(is_done)]):
                    observer.on_completed()

                has_value_all = all(has_value) # TODO: will this work?

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

    def __concat(self, *args):
        """Concatenates all the observable sequences. This takes in either an 
        array or variable arguments to concatenate.
     
        1 - concatenated = xs.concat(ys, zs)
        2 - concatenated = xs.concat([ys, zs])
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order. 
        """
        
        if isinstance(args[0], list):
            items = args[0]
        else:
            items = list(args)

        items.insert(0, self)
        return Observable.concat(items)
    
    @classmethod
    def concat(cls, *args):
        """Concatenates all the observable sequences.
    
        1 - res = Observable.concat(xs, ys, zs)
        2 - res = Observable.concat([xs, ys, zs])
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        
        if isinstance(args[0], list):
            sources = args[0]
        else:
            sources = list(args)
        
        return concat(Enumerable.for_each(sources))

    def concat_all(self):
        """Concatenates an observable sequence of observable sequences.
        
        Returns an observable sequence that contains the elements of each 
        observed inner sequence, in sequential order.
        """
        return self.merge(1)

    def __merge(self, max_concurrent_or_other):
        """Merges an observable sequence of observable sequences into an 
        observable sequence, limiting the number of concurrent subscriptions
        to inner sequences. Or merges two observable sequences into a single 
        observable sequence.
         
        1 - merged = sources.merge(1)
        2 - merged = source.merge(otherSource)  
         
        max_concurrent_or_other [Optional] Maximum number of inner observable 
            sequences being subscribed to concurrently or the second 
            observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences. 
        """
        if isinstance(max_concurrent_or_other, int):
            return Observable.merge(max_concurrent_or_other)
        
        sources = self

        def subscribe(observer):
            active_count = 0
            group = CompositeDisposable()
            is_stopped = False
            q = []
            
            def subscribe(xs):
                subscription = SingleAssignmentDisposable()
                group.add(subscription)
                
                def on_completed():
                    nonlocal active_count
                    
                    group.remove(subscription)
                    if q.length > 0:
                        s = q.shift()
                        subscribe(s)
                    else:
                        active_count -= 1
                        if is_stopped and active_count == 0:
                            observer.on_completed()
                        
                subscription.disposable = xs.subscribe(observer.on_next, observer.on_error, on_completed)
            
            def on_next(inner_source):
                nonlocal active_count

                if active_count < max_concurrent_or_other:
                    active_count += 1
                    subscribe(inner_source)
                else:
                    q.push(inner_source)

            def on_completed():
                nonlocal is_stopped

                is_stopped = True
                if active_count == 0:
                    observer.on_completed()
            
            group.add(sources.subscribe(on_next, observer.on_error, on_completed))
            return group
        return AnonymousObservable(subscribe)

    @classmethod
    def merge(cls, *args):
        """Merges all the observable sequences into a single observable 
        sequence. The scheduler is optional and if not specified, the 
        immediate scheduler is used.
     
        1 - merged = rx.Observable.merge(xs, ys, zs)
        2 - merged = rx.Observable.merge([xs, ys, zs])
        3 - merged = rx.Observable.merge(scheduler, xs, ys, zs)
        4 - merged = rx.Observable.merge(scheduler, [xs, ys, zs])    
     
        Returns the observable sequence that merges the elements of the observable sequences. 
        """
    
        if not args[0]:
            scheduler = immediate_scheduler
            sources = args[1:]
        elif args[0].now:
            scheduler = args[0]
            sources = args[1:]
        else:
            scheduler = immediate_scheduler
            sources = args[0]
        
        if isinstance(sources[0], list):
            sources = sources[0]
        
        return Observable.from_array(sources, scheduler).merge_observable()

    def merge_all(self):
        """Merges an observable sequence of observable sequences into an 
        observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences.   
        """
        sources = self

        def subscribe(observer):
            group = CompositeDisposable()
            is_stopped = False
            m = SingleAssignmentDisposable()
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_next(x):
                    observer.on_next(x)
                
                def on_completed():
                    group.remove(inner_subscription)
                    if is_stopped and group.length == 1:
                        observer.on_completed()
                    
                inner_subscription.disposable = inner_source.subscribe(on_next, observer.on_error, on_completed)
            
            def on_completed():
                is_stopped = True
                if len(group) == 1:
                    observer.on_completed()

            m.disposable = sources.subscribe(on_next, observer.on_error, on_completed)
            return group

        return AnonymousObservable(subscribe)

    def merge_observable(self):
        """Merges an observable sequence of observable sequences into an 
        observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences.        
        """
        sources = self

        def subscribe(observer):
            m = SingleAssignmentDisposable()
            group = CompositeDisposable()
            is_stopped = False
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_complete():
                    nonlocal group
                    
                    group.remove(inner_subscription)
                    if is_stopped and group.length == 1:
                        observer.on_completed()
                    
                disposable = inner_source.subscribe(
                    observer.on_next,
                    observer.on_error, 
                    on_complete)
                
                inner_subscription.disposable = disposable
            
            def on_complete():
                nonlocal is_stopped

                is_stopped = True
                if group.length == 1:
                    observer.on_completed()
            
            m.disposable = sources.subscribe(on_next, observer.on_error, on_complete)
            return group
        
        return AnonymousObservable(subscribe)

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
            pos = 0
            
            def action(this, state=None):
                nonlocal pos

                if pos < len(sources):
                    current = sources[pos]
                    pos += 1
                    d = SingleAssignmentDisposable()
                    subscription.disposable = d
                    d.disposable = current.subscribe(observer.on_next, lambda ex: this(), lambda: this())
                else:
                    observer.on_completed()
                
            cancelable = immediate_scheduler.schedule_recursive(action)
            return CompositeDisposable(subscription, cancelable)
        return AnonymousObservable(subscribe)

    def switch_latest(self):
        """Transforms an observable sequence of observable sequences into an 
        observable sequence producing values only from the most recent 
        observable sequence.
        
        Returns the observable sequence that at any point in time produces the 
        elements of the most recent inner observable sequence that has been received.  
        """
    
        sources = self

        def subscribe(observer):
            has_latest = False
            inner_subscription = SerialDisposable()
            is_stopped = False
            latest = 0

            def on_next(inner_source):
                nonlocal latest, has_latest

                d = SingleAssignmentDisposable()
                latest += 1
                _id = latest
                has_latest = True
                inner_subscription.disposable = d

                def on_next(x):
                    if latest == _id:
                        observer.on_next(x)
                
                def on_error(e):
                    if latest == _id:
                        observer.on_error(e)
                
                def on_completed():
                    nonlocal has_latest

                    if latest == _id:
                        has_latest = False
                        if is_stopped:
                            observer.on_completed()
                        
                d.disposable = inner_source.subscribe(on_next, on_error, on_completed)
            
            def on_completed():
                nonlocal is_stopped

                is_stopped = True
                if not has_latest:
                    observer.on_completed()
                
            subscription = sources.subscribe(on_next, observer.on_error, on_completed)
            return CompositeDisposable(subscription, inner_subscription)
        return AnonymousObservable(subscribe)

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
            is_open = False

            def on_next(left):
                if is_open:
                    observer.on_next(left)
            
            def on_completed():
                if is_open:
                    observer.on_completed()
            
            disposables = CompositeDisposable(source.subscribe(on_next, observer.on_error, on_completed))

            right_subscription = SingleAssignmentDisposable()
            disposables.add(right_subscription)

            def on_next2(x):
                nonlocal is_open

                is_open = True
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
            index = 0
            
            def on_next(left):
                nonlocal index

                if index < length:
                    right = second[index]
                    index += 1
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
            queues = [[]] * n
            is_done = [False] * n
            
            def next(i):
                if all([len(q) for q in queues]):
                    try:
                        queued_values = [x.pop(0) for x in queues]
                        res = result_selector(parent, queued_values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    
                    observer.on_next(res)
                elif all([j != i for j, x in enumerate(is_done)]):
                    observer.on_completed()
                
            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()

            subscriptions = [None]*n

            def func(i):
                subscriptions[i] = SingleAssignmentDisposable()

                def on_next(x):
                    queues[i].push(x)
                    next(i)
                
                subscriptions[i].disposable = sources[i].subscribe(on_next, observer.on_error, lambda: done(i))
                
            for idx in range(n):
                func(idx)

            return CompositeDisposable(subscriptions)
        return AnonymousObservable(subscribe)
