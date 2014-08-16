from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableZipArray(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def __init__(self, subscribe):
        self.zip_array = self.__zip_array # Stitch in instance method

    def __zip_array(self, second, result_selector):
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
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    observer.on_next(result)
                else:
                    observer.on_completed()

            return first.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    @classmethod
    def zip_array(cls, *args):
        """Merges the specified observable sequences into one observable
        sequence by emitting a list with the elements of the observable
        sequences at corresponding indexes.

        Keyword arguments:
        args -- Observable sources.

        Returns an observable {Observable} sequence containing lists of elements
        at corresponding indexes."""

        sources = args

        sources = list(args)
        result_selector = sources.pop()
        sources.insert(0, parent)

        def subscribe(observer):
            n = len(sources)
            queues = [[] for _ in range(n)]
            is_done = [False] * n

            def next(i):
                if all([len(q) for q in queues]):
                    res = [x.pop(0) for x in queues]
                    observer.on_next(res)
                elif all([x for j, x in enumerate(is_done) if j != i]):
                    observer.on_completed()
                    return

            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()
                    return

            subscriptions = [None]*n

            def func(i):
                subscriptions[i] = SingleAssignmentDisposable()

                def on_next(x):
                    queues[i].append(x)
                    next(i)

                subscriptions[i].disposable = sources[i].subscribe(on_next, observer.on_error, lambda: done(i))
            for idx in range(n):
                func(idx)

            composite_disposable = CompositeDisposable(subscriptions)

            def action():
                queues = [[] for _ in queues]

            composite_disposable.add(Disposable.create(action))

            return composite_disposable
        return AnonymousObservable(subscribe)
