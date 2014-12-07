from rx import AnonymousObservable, Observable
from rx.internal.basic import identity
from rx.internal.exceptions import SequenceContainsNoElementsError
from rx.internal import extends

from .min import first_only

@extends(Observable)
class Max(object):


    def max(self, comparer=None):
        """Returns the maximum value in an observable sequence according to the
        specified comparer.

        Example
        res = source.max()
        res = source.max(lambda x, y:  x.value - y.value)

        Keyword arguments:
        comparer -- {Function} [Optional] Comparer used to compare elements.

        Returns {Observable} An observable sequence containing a single element
        with the maximum element in the source sequence.
        """

        return self.max_by(identity, comparer).select(lambda x: first_only(x))
