from rx.concurrency import current_thread_scheduler
from rx.internal import extends

from .controlledobservable import ControlledObservable
from .stopandwaitobservable import StopAndWaitObservable

@extends(ControlledObservable)
class ControlledObservableStopAndWait(object):


    def stop_and_wait(self, scheduler):
        """Attaches a stop and wait observable to the current observable.

        scheduler -- {Scheduler} [Optional] Optional scheduler used for yielding
            values.

        Returns a stop and wait observable {Observable}.
        """

        scheduler = scheduler or current_thread_scheduler
        return StopAndWaitObservable(self, scheduler)
