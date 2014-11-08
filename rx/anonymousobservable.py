from rx.disposables import Disposable
from .autodetachobserver import AutoDetachObserver
from .abstractobserver import AbstractObserver
from .observable import Observable

class AnonymousObservable(Observable):
    """Class to create an Observable instance from a delegate-based 
    implementation of the Subscribe method."""
    
    def __init__(self, subscribe):
        """Creates an observable sequence object from the specified subscription 
        function.

        Keyword arguments:
        subscribe -- Subscribe method implementation."""
        
        def _subscribe(observer):
            """Decorator for subscribe. It wraps the observer in an 
            AutoDetachObserver and fixes the returned disposable"""

            def fix_subscriber(subscriber):
                """Fixes subscriber to make sure it returns a Disposable instead
                of None or a dispose function"""
            
                if subscriber is None:
                    subscriber = Disposable()
                elif not hasattr(subscriber, "dispose"):
                    subscriber = Disposable(subscriber)
                return subscriber

            auto_detach_observer = AutoDetachObserver(observer)
            try:
                auto_detach_observer.disposable = fix_subscriber(subscribe(auto_detach_observer))
            except Exception as ex:
                if not auto_detach_observer.fail(ex):
                    raise ex
            return auto_detach_observer
        
        super(AnonymousObservable, self).__init__(_subscribe)
