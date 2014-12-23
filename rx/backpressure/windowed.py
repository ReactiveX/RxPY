from rx.concurrency import current_thread_scheduler
from rx.internal import extensionmethod

from .controlledobservable import ControlledObservable
from .windowedobservable import WindowedObservable

@extensionmethod(ControlledObservable)
def windowed(self, window_size):
    """Creates a sliding windowed observable based upon the window size.


    window_size -- {Number} The number of items in the window

    Returns a windowed observable {Observable} based upon the window size.
    """

    return WindowedObservable(self, window_size)