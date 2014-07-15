import types
import logging

from rx.concurrency import current_thread_scheduler
from rx.disposables import Disposable
from .autodetachobserver import AutoDetachObserver
from .observable import Observable

log = logging.getLogger("Rx")

class AnonymousObservable(Observable):
    """Class to create an Observable instance from a delegate-based 
    implementation of the Subscribe method."""
    
    @staticmethod
    def fix_subscriber(subscriber):
        """Fix subscriber to check for None or function returned to decorate as Disposable"""
    
        if subscriber is None:
            subscriber = Disposable.empty()
        elif type(subscriber) == types.FunctionType:
            subscriber = Disposable(subscriber)

        return subscriber

    def __init__(self, subscribe):
        """Creates an observable sequence object from the specified subscription 
        function.

        Keyword arguments:
        subscribe -- Subscribe method implementation.
        """
        def _subscribe(observer):
            auto_detach_observer = AutoDetachObserver(observer)

            # Backup. Kick queue if there's anything left: TODO: can we move this somewhere else?
            if current_thread_scheduler.schedule_required():
                def action(scheduler, state=None):
                    try:
                        auto_detach_observer.disposable = self.fix_subscriber(subscribe(auto_detach_observer))
                    except Exception as ex:
                        if not auto_detach_observer.fail(ex):
                            raise ex
                current_thread_scheduler.schedule(action)
            else:
                try:
                    auto_detach_observer.disposable = self.fix_subscriber(subscribe(auto_detach_observer))
                except Exception as ex:
                    log.error("AnonymousObservable Exception: %s" % ex)
                    
                    if not auto_detach_observer.fail(ex):
                        raise ex

            return auto_detach_observer
        
        super(AnonymousObservable, self).__init__(_subscribe)
    