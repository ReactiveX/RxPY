from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableNever(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def never(cls):
        """Returns a non-terminating observable sequence, which can be used to 
        denote an infinite duration (e.g. when using reactive joins).
     
        Returns an observable sequence whose observers will never get called.
        """
        def subscribe(_):
            return Disposable.empty()

        return AnonymousObservable(subscribe)
