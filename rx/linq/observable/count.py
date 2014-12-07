from rx import Observable
from rx.internal import extends

@extends(Observable)
class Count(object):


    def count(self, predicate=None):
        """Returns an observable sequence containing a value that represents
        how many elements in the specified observable sequence satisfy a
        condition if provided, else the count of items.

        1 - res = source.count()
        2 - res = source.count(lambda x: x > 3)

        Keyword arguments:
        predicate -- [Optional] A function to test each element for a condition.

        Returns an observable sequence containing a single element with a
        number that represents how many elements in the input sequence satisfy
        the condition in the predicate function if provided, else the count of
        items in the sequence.
        """

        if predicate:
            return self.where(predicate).count()
        else:
            return self.aggregate(lambda count, _: count + 1, seed=0)
