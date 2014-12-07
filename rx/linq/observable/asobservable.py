from rx import AnonymousObservable, Observable
from rx.internal import extends


@extends(Observable)
class AsObservable(object):

    def as_observable(self):
        """Hides the identity of an observable sequence.

        Returns an observable {Observable} sequence that hides the identity of
        the source sequence."""

        source = self

        def subscribe(observer):
            return source.subscribe(observer)

        return AnonymousObservable(subscribe)

