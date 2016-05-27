from datetime import datetime, timedelta

from rx.core import Scheduler, Disposable
from rx.disposables import CompositeDisposable
from rx.internal.basic import default_now


class SchedulerBase(Scheduler):
    """Provides a set of static properties to access commonly used
    schedulers.
    """

    def invoke_action(self, action, state=None):
        ret = action(self, state)
        if isinstance(ret, Disposable):
            return ret

        return Disposable.empty()

    @property
    def now(self):
        """Represents a notion of time for this scheduler. Tasks being
        scheduled on a scheduler will adhere to the time denoted by this
        property.
        """

        return default_now()

    @classmethod
    def to_relative(cls, timespan):
        """Converts time value to milliseconds"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.fromtimestamp(0)
            timespan = int(timespan.total_seconds()*1000)
        elif isinstance(timespan, timedelta):
            timespan = int(timespan.total_seconds()*1000)

        return int(timespan)

    @classmethod
    def to_datetime(cls, duetime):
        """Converts time value to datetime"""

        if isinstance(duetime, timedelta):
            duetime = datetime.fromtimestamp(0) + duetime
        elif not isinstance(duetime, datetime):
            duetime = datetime.fromtimestamp(duetime/1000.0)

        return duetime

    @classmethod
    def to_timedelta(cls, timespan):
        """Converts time value to timedelta"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.fromtimestamp(0)
        elif not isinstance(timespan, timedelta):
            timespan = timedelta(milliseconds=timespan)

        return timespan

    @classmethod
    def normalize(cls, timespan):
        """Normalizes the specified timespan value to a positive value.

        Keyword arguments:
        :param int|timedelta timespan: The time span value to normalize.

        :returns: The specified Timespan value if it is zero or positive;
            otherwise, 0
        :rtype: int|timedelta
        """

        nospan = 0 if isinstance(timespan, int) else timedelta(0)
        if not timespan or timespan < nospan:
            timespan = nospan

        return timespan
