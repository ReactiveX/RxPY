from rx.internal.basic import default_comparer
from rx.core.notification import OnNext, OnCompleted, OnError


class Recorded(object):
    def __init__(self, time, value, comparer=None):
        self.time = time
        self.value = value
        self.comparer = comparer or default_comparer

    def __eq__(self, other):
        """Returns true if a recorded value matches another recorded value"""

        time_match = self.time == other.time
        return time_match and self.comparer(self.value, other.value)

    equals = __eq__

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s@%s" % (self.value, self.time)


def _mk_is_action_check(action_type):
    """Create a function that checks whether a Recorded instance has a
    notification of type ``action_type``.

    :type action_type: rx.core.notification.Notification
    """
    def is_action(recorded):
        return isinstance(recorded.value, action_type)
    return is_action


is_next = _mk_is_action_check(OnNext)


is_completed = _mk_is_action_check(OnCompleted)


is_error = _mk_is_action_check(OnError)
