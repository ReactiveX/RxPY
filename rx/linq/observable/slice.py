from rx import Observable
from rx.internal import extends


@extends(Observable)
class Slice(object):

    def slice(self, start=None, stop=None, step=1):
        """Slices the given observable. It is basically a wrapper around the
        operators skip(), skip_last(), take(), take_last() and filter().

        This marble diagram helps you remember how slices works with streams.
        Positive numbers is relative to the start of the events, while negative
        numbers are reliative to the end (on_completed) of the stream.

        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1

        Example:
        result = source.slice(1, 10)
        result = source.slice(1, -2)
        result = source.slice(1, -1, 2)

        Keyword arguments:
        start -- Number of elements to skip of take last
        stop -- Last element to take of skip last
        step -- Takes every step element. Must be larger than zero

        Returns {Observable} a sliced observable sequence.
        """

        source = self

        if not start is None:
            if start < 0:
                source = source.take_last(abs(start))
            else:
                source = source.skip(start)

        if not stop is None:
            if stop > 0:
                start = start or 0
                source = source.take(stop-start)
            else:
                source = source.skip_last(abs(stop))

        if not step is None:
            if step > 1:
                source = source.filter(lambda x, i: i % step == 0)
            else:
                # Reversing events is not supported
                raise TypeError("Negative step not supported.")

        return source

    def __getitem__(self, key):
        """Slices the given observable using Python slice notation. The
        arguments to slice is start, stop and step given within brackets [] and
        separated with the ':' character. It is basically a wrapper around the
        operators skip(), skip_last(), take(), take_last() and filter().

        This marble diagram helps you remember how slices works with streams.
        Positive numbers is relative to the start of the events, while negative
        numbers are reliative to the end (on_completed) of the stream.

        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1

        Example:
        result = source[1:10]
        result = source[1:-2]
        result = source[1:-1:2]

        Keyword arguments:
        key -- Slice object

        Returns {Observable} a sliced observable sequence.
        """

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
        elif isinstance(key, int):
            start, stop, step = key, key+1, 1
        else:
            raise TypeError("Invalid argument type.")

        return self.slice(start, stop, step)