from six import add_metaclass

from rx.concurrency import Scheduler
from rx.observable import Observable

from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableStart(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def start(cls, func, scheduler=None):
        """Invokes the specified function asynchronously on the specified
        scheduler, surfacing the result through an observable sequence.

        Example:
        res = rx.Observable.start(lambda: pprint('hello'))
        res = rx.Observable.start(lambda: pprint('hello'), rx.Scheduler.timeout)

        Keyword arguments:
        func -- {Function} Function to run asynchronously.
        scheduler -- {Scheduler} [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.

        Returns {Observable} An observable sequence exposing the function's
        result value, or an exception.

        Remarks:
        The function is called immediately, not during the subscription of the
        resulting sequence. Multiple subscriptions to the resulting sequence can
        observe the function's result."""

        return Observable.to_async(func, scheduler)()
