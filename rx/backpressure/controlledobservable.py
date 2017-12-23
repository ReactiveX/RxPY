from rx.core import ObservableBase

from .controlledsubject import ControlledSubject
from .stopandwaitobservable import StopAndWaitObservable
from .windowedobservable import WindowedObservable


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

    def stop_and_wait(self):
        """Attaches a stop and wait observable to the current observable.

        :returns: A stop and wait observable.
        :rtype: Observable
        """

        return StopAndWaitObservable(self)

    def windowed(self, window_size):
        """Creates a sliding windowed observable based upon the window size.

        Keyword arguments:
        :param int window_size: The number of items in the window

        :returns: A windowed observable based upon the window size.
        :rtype: Observable
        """

        return WindowedObservable(self, window_size)
