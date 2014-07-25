from six import add_metaclass
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableCreate(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def create(cls, subscribe):
        return AnonymousObservable(subscribe)

    # Deprecated alias
    create_with_disposable = create 
