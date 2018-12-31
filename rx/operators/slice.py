from rx.core import Observable

# pylint: disable=w0622


def slice(source, start: int = None, stop: int = None, step: int = 1) -> Observable:
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

    has_start = start is not None
    has_stop = stop is not None
    has_step = step is not None

    if has_stop and stop >= 0:
        source = source.take(stop)

    if has_start and start > 0:
        source = source.skip(start)

    if has_start and start < 0:
        source = source.take_last(abs(start))

    if has_stop and stop < 0:
        source = source.skip_last(abs(stop))

    if has_step:
        if step > 1:
            source = source.filteri(lambda x, i: i % step == 0)
        elif step < 0:
            # Reversing events is not supported
            raise TypeError("Negative step not supported.")

    return source
