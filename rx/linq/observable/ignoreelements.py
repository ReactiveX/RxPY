from rx import Observable, AnonymousObservable
from rx.internal import noop
from rx.internal import extends


@extends(Observable)
class IgnoreElements(object):

    def ignore_elements(self):
        """Ignores all elements in an observable sequence leaving only the
        termination messages.

        Returns an empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
        """

        source = self

        def subscribe(observer):
            return source.subscribe(noop, observer.on_error, observer.on_completed)

        return AnonymousObservable(subscribe)
