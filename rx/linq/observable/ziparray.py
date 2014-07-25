from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableZipArray(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def zip_array(self, second, result_selector):
        first = self

        def subscribe(observer):
            length = len(second)
            index = [0]
            
            def on_next(left):
                if index[0] < length:
                    right = second[index[0]]
                    index[0] += 1
                    try:
                        result = result_selector(left, right)
                    except Exception as e:
                        observer.on_error(e)
                        return
                    
                    observer.on_next(result)
                else:
                    observer.on_completed()
                
            return first.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
