from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable
from rx.concurrency import immediate_scheduler, current_thread_scheduler

class ObservableDefer:
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def defer(cls, observable_factory):
        """Returns an observable sequence that invokes the specified factory
        function whenever a new observer subscribes.

        Example:
        1 - res = rx.Observable.defer(lambda: rx.Observable.from_array([1,2,3]))

        Keyword arguments:
        observable_factory -- Observable factory function to invoke for each
            observer that subscribes to the resulting sequence.

        Returns an observable sequence whose observers trigger an invocation
        of the given observable factory function."""

        def subscribe(observer):
            result = None
            try:
                result = observable_factory()
            except Exception as ex:
                return Observable.throw_exception(ex).subscribe(observer)

            result = Observable.from_future(result)
            return result.subscribe(observer)
        return AnonymousObservable(subscribe)

Observable.defer = ObservableDefer.defer