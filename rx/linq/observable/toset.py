from rx import Observable, AnonymousObservable
from rx.internal import extends

def to_set(source, set_type):
    def subscribe(observer):
        s = set_type()

        def on_completed():
            observer.on_next(s)
            observer.on_completed()

        return source.subscribe(s.add, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)


@extends(Observable)
class ToSet(object):

    def to_set(self):
        """Converts the observable sequence to a set.

        Returns {Observable} An observable sequence with a single value of a set
        containing the values from the observable sequence.
        """

        return to_set(self, set)
