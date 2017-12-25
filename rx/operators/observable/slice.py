from rx.core import ObservableBase


def slice(source, start: int = None, stop: int = None, step: int = 1) -> ObservableBase:
    """Slices the given observable. It is basically a wrapper around the
    operators skip(), skip_last(), take(), take_last() and filter().

    This marble diagram helps you remember how slices works with streams.
    Positive numbers is relative to the start of the events, while negative
    numbers are relative to the end (close) of the stream.

    r---e---a---c---t---i---v---e---|
    0   1   2   3   4   5   6   7   8
   -8  -7  -6  -5  -4  -3  -2  -1   0

    Example:
    result = source.slice(1, 10)
    result = source.slice(1, -2)
    result = source.slice(1, -1, 2)

    Keyword arguments:
    source -- Observable to slice
    start -- Number of elements to skip of take last
    stop -- Last element to take of skip last
    step -- Takes every step element. Must be larger than zero

    Returns a sliced observable sequence.
    """

    if start is not None:
        if start < 0:
            source = source.take_last(abs(start))
        else:
            source = source.skip(start)

    if stop is not None:
        if stop > 0:
            start = start or 0
            source = source.take(stop - start)
        else:
            source = source.skip_last(abs(stop))

    if step is not None:
        if step > 1:
            source = source.filter(predicate_indexed=lambda x, i: i % step == 0)
        elif step < 0:
            # Reversing events is not supported
            raise TypeError("Negative step not supported.")

    return source
