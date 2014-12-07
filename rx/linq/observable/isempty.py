from rx import AnonymousObservable, Observable
from rx.internal import extends

@extends(Observable)
class IsEmpty(object):


    def is_empty(self):
        """Determines whether an observable sequence is empty.

        Returns an observable {Observable} sequence containing a single element
        determining whether the source sequence is empty.
        """

        return self.some().select(lambda b: not b)

