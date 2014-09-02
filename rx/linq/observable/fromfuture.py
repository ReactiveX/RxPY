from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableCreation(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def from_future(future):
        """Converts a Future to an Observable sequence

        Keyword Arguments:
        future -- {Future} A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future

        Returns {Observable} An Observable sequence which wraps the existing
        future success and failure."""

        def subscribe(observer):
            def done():
                try:
                    value = future.result()
                except Exception as ex:
                    observer.on_error(ex)
                else:
                    observer.on_next(value)
                    observer.on_completed()
                    
            future.add_done_callback(done)
            
            def dispose():
                if future and future.cancel:
                  promise.cancel()
            return dispose

        return AnonymousObservable(subscribe)
