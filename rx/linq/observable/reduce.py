from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableReduce(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def reduce(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence,
        returning the result of the aggregation as a single element in the
        result sequence. The specified seed value is used as the initial
        accumulator value.

        For aggregation behavior with incremental intermediate results, see
        Observable.scan.

        Example:
        1 - res = source.reduce(lambda acc, x: acc + x)
        2 - res = source.reduce(lambda acc, x: acc + x, 0)

        Keyword arguments:
        accumulator -- {Function}  An accumulator function to be invoked on each
            element.
        seed -- {Any} [Optional] The initial accumulator value.

        Returns {Observable} An observable sequence containing a single element
        with the final accumulator value."""

        if not seed is None:
            return self.scan(accumulator, seed=seed).start_with(seed).last()
        else:
            return self.scan(accumulator).last()
