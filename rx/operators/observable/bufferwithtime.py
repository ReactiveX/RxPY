from rx.core import ObservableBase


def buffer_with_time(source, timespan, timeshift=None) -> ObservableBase:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on timing information.

    # non-overlapping segments of 1 second
    1 - res = xs.buffer_with_time(1000)
    # segments of 1 second with time shift 0.5 seconds
    2 - res = xs.buffer_with_time(1000, 500)

    Keyword arguments:
    source -- Observable sequence.
    timespan -- Length of each buffer (specified as an integer denoting
        milliseconds).
    timeshift -- [Optional] Interval between creation of consecutive
        buffers (specified as an integer denoting milliseconds), or an
        optional scheduler parameter. If not specified, the time shift
        corresponds to the timespan parameter, resulting in non-overlapping
        adjacent buffers.

    Returns an observable sequence of buffers.
    """

    if not timeshift:
        timeshift = timespan

    return source.window_with_time(timespan, timeshift).flat_map(lambda x: x.to_iterable())
