from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableBufferWithTime(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def buffer_with_time(self, timespan, timeshift=None, scheduler=None):
        """Projects each element of an observable sequence into zero or more
        buffers which are produced based on timing information.

        1 - res = xs.buffer_with_time(1000) # non-overlapping segments of 1 second
        2 - res = xs.buffer_with_time(1000, 500) # segments of 1 second with time shift 0.5 seconds

        Keyword arguments:
        timespan -- Length of each buffer (specified as an integer denoting
            milliseconds).
        timeshift -- [Optional] Interval between creation of consecutive
            buffers (specified as an integer denoting milliseconds), or an
            optional scheduler parameter. If not specified, the time shift
            corresponds to the timespan parameter, resulting in non-overlapping
            adjacent buffers.
        scheduler -- [Optional] Scheduler to run buffer timers on. If not
            specified, the timeout scheduler is used.

        Returns an observable sequence of buffers.
        """
        if not timeshift:
            timeshift = timespan

        scheduler = scheduler or timeout_scheduler

        return self.window_with_time(timespan, timeshift, scheduler) \
            .select_many(lambda x: x.to_array())