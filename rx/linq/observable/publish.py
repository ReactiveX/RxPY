from rx import Observable, AnonymousObservable
from rx.subjects import Subject
from rx.internal import extends

@extends(Observable)
class Publish(object):


    def publish(self, selector=None):
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
            return self.multicast(subject_selector=lambda: Subject(), selector=selector)
        else:
            return self.multicast(subject=Subject())
