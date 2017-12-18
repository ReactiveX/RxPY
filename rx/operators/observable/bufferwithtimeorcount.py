from rx.core import ObservableBase


def buffer_with_time_or_count(source, timespan, count) -> ObservableBase:
    """Projects each element of an observable sequence into a buffer that
    is completed when either it's full or a given amount of time has
    elapsed.

    # 5s or 50 items in an array
    1 - res = source.buffer_with_time_or_count(5000, 50)
    # 5s or 50 items in an array
    2 - res = source.buffer_with_time_or_count(5000, 50, Scheduler.timeout)

    Keyword arguments:
    timespan -- Maximum time length of a buffer.
    count -- Maximum element count of a buffer.
    scheduler -- [Optional] Scheduler to run bufferin timers on. If not
        specified, the timeout scheduler is used.

    Returns an observable sequence of buffers.
    """

    return source.window_with_time_or_count(timespan, count).flat_map(lambda x: x.to_iterable())
