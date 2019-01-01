from typing import Callable
from rx.core import Observable, AnonymousObservable


def _to_dict(source, map_type, key_mapper, element_mapper):
    def subscribe(observer, scheduler=None):
        m = map_type()

        def on_next(x):
            try:
                key = key_mapper(x)
            except Exception as ex:
                observer.on_error(ex)
                return

            element = x
            if element_mapper:
                try:
                    element = element_mapper(x)
                except Exception as ex:
                    observer.on_error(ex)
                    return

            m[key] = element

        def on_completed():
            observer.on_next(m)
            observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
    return AnonymousObservable(subscribe)


def to_dict(key_mapper, element_mapper=None) -> Callable[[Observable], Observable]:
    """Converts the observable sequence to a Map if it exists.

    Keyword arguments:
    key_mapper -- A function which produces the key for the
        dictionary.
    element_mapper -- [Optional] An optional function which produces
        the element for the dictionary. If not present, defaults to the
        value from the observable sequence.

    Returns an observable sequence with a single value of a dictionary
    containing the values from the observable sequence.
    """

    def partial(source: Observable) -> Observable:
        return _to_dict(source, dict, key_mapper, element_mapper)
    return partial
