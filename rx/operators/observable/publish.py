from rx.core import ObservableBase
from rx.subjects import Subject


def publish(source, selector=None) -> ObservableBase:
    """Returns an observable sequence that is the result of invoking the
    selector on a connectable observable sequence that shares a single
    subscription to the underlying sequence. This operator is a
    specialization of Multicast using a regular Subject.

    Example:
    res = source.publish()
    res = source.publish(lambda x: x)

    selector -- {Function} [Optional] Selector function which can use the
        multicasted source sequence as many times as needed, without causing
        multiple subscriptions to the source sequence. Subscribers to the
        given source will receive all notifications of the source from the
        time of the subscription on.

    Returns an observable {Observable} sequence that contains the elements
    of a sequence produced by multicasting the source sequence within a
    selector function."""

    if selector:
        return source.multicast(subject_selector=lambda _: Subject(), selector=selector)
    else:
        return source.multicast(subject=Subject())

def share(source) -> ObservableBase:
    """Share a single subscription among multple observers.

    Returns a new Observable that multicasts (shares) the original
    Observable. As long as there is at least one Subscriber this
    Observable will be subscribed and emitting data. When all
    subscribers have unsubscribed it will unsubscribe from the source
    Observable.

    This is an alias for Observable.publish().ref_count().
    """
    return source.publish().ref_count()
