from rx.core import ObservableBase, AnonymousObservable


def _to_dict(source, map_type, key_mapper, element_mapper):
    def subscribe(observer, scheduler=None):
        m = map_type()

        def send(x):
            try:
                key = key_mapper(x)
            except Exception as ex:
                observer.throw(ex)
                return

            element = x
            if element_mapper:
                try:
                    element = element_mapper(x)
                except Exception as ex:
                    observer.throw(ex)
                    return

            m[key] = element

        def close():
            observer.send(m)
            observer.close()

        return source.subscribe_(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)


def to_dict(self, key_mapper, element_mapper=None) -> ObservableBase:
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

    return _to_dict(self, dict, key_mapper, element_mapper)

