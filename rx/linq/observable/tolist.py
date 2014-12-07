from rx.observable import Observable
from rx.internal import extends

@extends(Observable)
class ToList(object):


    def to_list(self):
        """Creates a list from an observable sequence.

        Returns an observable sequence containing a single element with a list
        containing all the elements of the source sequence."""

        def accumulator(res, i):
            res.append(i)
            return res[:]

        return self.scan(accumulator, seed=[]).start_with([]).last()

    to_array = to_iterable = to_list