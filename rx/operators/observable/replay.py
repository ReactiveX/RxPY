from rx.core import ObservableBase
from rx.subjects import ReplaySubject


def replay(self, mapper=None, buffer_size=None, window=None, scheduler=None) -> ObservableBase:
    """Returns an observable sequence that is the result of invoking the
    mapper on a connectable observable sequence that shares a single
    subscription to the underlying sequence replaying notifications subject
    to a maximum time length for the replay buffer.

    This operator is a specialization of Multicast using a ReplaySubject.

    Example:
    res = source.replay(buffer_size=3)
    res = source.replay(buffer_size=3, window=500)
    res = source.replay(None, 3, 500)
    res = source.replay(lambda x: x.take(6).repeat(), 3, 500)

    Keyword arguments:
    mapper -- [Optional] Selector function which can use the multicasted
        source sequence as many times as needed, without causing multiple
        subscriptions to the source sequence. Subscribers to the given
        source will receive all the notifications of the source subject to
        the specified replay buffer trimming policy.
    buffer_size -- [Optional] Maximum element count of the replay buffer.
    window -- [Optional] Maximum time length of the replay buffer.

    Returns {Observable} An observable sequence that contains the elements
    of a sequence produced by multicasting the source sequence within a
    mapper function.
    """


    if mapper:
        def subject_mapper(scheduler):
            return ReplaySubject(buffer_size, window, scheduler)
        return self.multicast(subject_mapper=subject_mapper,mapper=mapper)

    return self.multicast(ReplaySubject(buffer_size, window, scheduler))
