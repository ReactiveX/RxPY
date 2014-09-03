from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableBufferWithTime(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def buffer_with_time_or_count(self, timespan, count, scheduler):
        """Projects each element of an observable sequence into a buffer that
        is completed when either it's full or a given amount of time has
        elapsed.

        1 - res = source.bufferWithTimeOrCount(5000, 50); # 5s or 50 items in an array
        2 - res = source.bufferWithTimeOrCount(5000, 50, Scheduler.timeout); # 5s or 50 items in an array

        Keyword arguments:
        timespan -- Maximum time length of a buffer.
        count -- Maximum element count of a buffer.
        scheduler -- [Optional] Scheduler to run bufferin timers on. If not
            specified, the timeout scheduler is used.

        Returns an observable sequence of buffers.
        """
        scheduler = scheduler or timeout_scheduler
        return self.window_with_time_or_count(timespan, count, scheduler) \
            .select_many(lambda x: x.to_array())
