from rx.core import Observable
from rx.internal import extensionmethod

from .controlledsubject import ControlledSubject


class ControlledObservable(Observable):

    def __init__(self, source, enable_queue, scheduler=None):
        super(ControlledObservable, self).__init__()

        self.subject = ControlledSubject(enable_queue, scheduler)
        self.source = source.multicast(self.subject).ref_count()

    def _subscribe_core(self, observer, scheduler=None):
        return self.source.subscribe(observer, scheduler)

    def request(self, number_of_items):
        if number_of_items is None:
            number_of_items = -1
        return self.subject.request(number_of_items)


@extensionmethod(Observable)
def controlled(self, enable_queue=True, scheduler=None):
    """Attach a controller to the observable sequence

    Attach a controller to the observable sequence with the ability to
    queue.

    Example:
    source = rx.Observable.interval(100).controlled()
    source.request(3) # Reads 3 values

    Keyword arguments:
    :param bool enable_queue: truthy value to determine if values should
        be queued pending the next request
    :param Scheduler scheduler: determines how the requests will be scheduled
    :returns: The observable sequence which only propagates values on request.
    :rtype: Observable
    """

    return ControlledObservable(self, enable_queue, scheduler)
