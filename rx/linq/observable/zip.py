from six import add_metaclass

from rx.internal import noop
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler
from rx.internal.enumerable import Enumerable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableZip(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def __init__(self, subscribe):
        self.zip = self.__zip # Stitch in instance method

    def __zip(self, *args):
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

        parent = self
        sources = list(args)
        result_selector = sources.pop()
        sources.insert(0, parent)

        if args and isinstance(args[0], list):
            return self.zip_array(*args)

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

    @classmethod
    def zip(cls, *args):
        """Merges the specified observable sequences into one observable 
        sequence by using the selector function whenever all of the observable 
        sequences have produced an element at a corresponding index.
        
        The last element in the arguments must be a function to invoke for each
        series of elements at corresponding indexes in the sources.

        Arguments:
        args -- Observable sources.
     
        Returns an observable {Observable} sequence containing the result of 
        combining elements of the sources using the specified result selector 
        function."""
        
        first = args.pop(0);
        return first.zip(*args)
