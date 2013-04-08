from rx.concurrency import current_thread_scheduler

from .autodetachobserver import AutoDetachObserver
from .observable import Observable

class AnonymousObservable(Observable):
    """Class to create an Observable instance from a delegate-based implementation
    of the Subscribe method."""
    
    def __init__(self, subscribe):
        """Creates an observable sequence object from the specified subscription function.

        Keyword arguments:
        subscribe -- Subscribe method implementation.
        """
        def _subscribe(observer):
            auto_detach_observer = AutoDetachObserver(observer)
            if current_thread_scheduler.schedule_required():
                def action(scheduler, state=None):
                    try:
                        auto_detach_observer.disposable = subscribe(auto_detach_observer)
                    except Exception as ex:
                        if not auto_detach_observer.fail(): #(ex):
                            raise ex
                current_thread_scheduler.schedule(action)
            else:
                try:
                    auto_detach_observer.disposable = subscribe(auto_detach_observer)
                except Exception as ex:
                    if not auto_detach_observer.fail(ex):
                        raise ex

            return auto_detach_observer
        
        super(AnonymousObservable, self).__init__(_subscribe)
    