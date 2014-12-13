from rx.concurrency import current_thread_scheduler
from rx.internal import extends

from .controlledobservable import ControlledObservable
from .stopandwaitobservable import StopAndWaitObservable


@extends(ControlledObservable)
class ControlledObservableStopAndWait(object):

    def stop_and_wait(self):
        """Attaches a stop and wait observable to the current observable.

        Returns a stop and wait observable {Observable}.
        """

        return StopAndWaitObservable(self)
