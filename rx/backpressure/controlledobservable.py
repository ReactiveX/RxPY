from rx.core import ObservableBase

from .controlledsubject import ControlledSubject


class ControlledObservable(ObservableBase):

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


def controlled(self, enable_queue: bool = True, scheduler=None) -> ControlledObservable:
    """Attach a controller to the observable sequence

    Attach a controller to the observable sequence with the ability to
    queue.

    Example:
    source = rx.Observable.interval(100).controlled()
    source.request(3) # Reads 3 values

    Keyword arguments:
    enable_queue -- truthy value to determine if values should
        be queued pending the next request
    scheduler -- determines how the requests will be scheduled
    Returns the observable sequence which only propagates values on request.
    """

    return
