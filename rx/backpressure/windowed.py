from six import add_metaclass

from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

from .controlledobservable import ControlledObservable
from .windowedobservable import WindowedObservable

@add_metaclass(ExtensionMethod)
class ControlledObservableWindowed(ControlledObservable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def windowed(self, window_size, scheduler=None):
        """Creates a sliding windowed observable based upon the window size.
         
         
        window_size -- {Number} The number of items in the window
        scheduler -- {Scheduler} [Optional] Optional scheduler used for 
            parameterization of concurrency. If not specified, defaults to 
            Scheduler.timeout.
        
        Returns a windowed observable {Observable} based upon the window size.
        """
        scheduler = scheduler or current_thread_scheduler
        return WindowedObservable(self, window_size, scheduler)