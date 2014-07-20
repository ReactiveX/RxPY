import types

from rx.concurrency import current_thread_scheduler
from rx.disposables import Disposable
from .autodetachobserver import AutoDetachObserver
from .observable import Observable

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
            def set_disposable():
                try:
                    auto_detach_observer.disposable = self.fix_subscriber(subscribe(auto_detach_observer))
                except Exception as ex:
                    if not auto_detach_observer.fail(ex):
                        raise ex

            auto_detach_observer = AutoDetachObserver(observer)

            if current_thread_scheduler.schedule_required():
                current_thread_scheduler.schedule(set_disposable)
            else:
                set_disposable()

            return auto_detach_observer
        
        super(AnonymousObservable, self).__init__(_subscribe)
