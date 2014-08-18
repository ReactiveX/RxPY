from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableFind(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @staticmethod
    def _find_value(source, predicate, yield_index):
        def subscribe(observer):
            i = [0]

            def on_next(x):
                should_run = False
                try:
                    should_run = predicate(x, i, source)
                except Exception as ex:
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(i[0] if yield_index else x)
                    observer.on_completed()
                else:
                    i[0] += 1

            def on_completed():
                observer.on_next(-1 if yield_index else None)
                observer.on_completed()

            return source.subscribe(on_next, observer.on_error, on_completed)
        return AnonymousObservable(subscribe)

    def find(self, predicate):
        """Searches for an element that matches the conditions defined by the
        specified predicate, and returns the first occurrence within the entire
        Observable sequence.

        Keyword arguments:
        predicate -- {Function} The predicate that defines the conditions of the
            element to search for.

        Returns an Observable {Observable} sequence with the first element that
        matches the conditions defined by the specified predicate, if found
        otherwise, None."""

        return self._find_value(self, predicate, False)
