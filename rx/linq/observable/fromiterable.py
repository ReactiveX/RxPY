from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableFromIterable(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def from_iterable(cls, iterable, scheduler=None):
        """Converts an array to an observable sequence, using an optional
        scheduler to enumerate the array.

        1 - res = rx.Observable.from_array([1,2,3])
        2 - res = rx.Observable.from_array([1,2,3], rx.Scheduler.timeout)

        Keyword arguments:
        scheduler -- [Optional] Scheduler to run the enumeration of the input
            sequence on.

        Returns the observable sequence whose elements are pulled from the
        given enumerable sequence."""

        scheduler = scheduler or current_thread_scheduler
        it = iter(iterable)

        def subscribe(observer):
            def action(action1, state=None):
                try:
                    item = next(it)
                except StopIteration:
                    observer.on_completed()
                else:
                    observer.on_next(item)
                    action1(action)

            return scheduler.schedule_recursive(action)
        return AnonymousObservable(subscribe)

    from_array = from_list = from_iterable # Compatibility