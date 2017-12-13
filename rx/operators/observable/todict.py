from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod

def _to_dict(source, map_type, key_selector, element_selector):
    def subscribe(observer, scheduler=None):
        m = map_type()

        def send(x):
            try:
                key = key_selector(x)
            except Exception as ex:
                observer.throw(ex)
                return

            element = x
            if element_selector:
                try:
                    element = element_selector(x)
                except Exception as ex:
                    observer.throw(ex)
                    return

            m[key] = element

        def close():
            observer.send(m)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def to_dict(self, key_selector, element_selector=None):
    """Converts the observable sequence to a Map if it exists.

    Keyword arguments:
    key_selector -- {Function} A function which produces the key for the
        Map.
    element_selector -- {Function} [Optional] An optional function which
        produces the element for the Map. If not present, defaults to the
        value from the observable sequence.
    Returns {Observable} An observable sequence with a single value of a Map
    containing the values from the observable sequence.
    """

    return _to_dict(self, dict, key_selector, element_selector)

