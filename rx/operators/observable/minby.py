from rx.core import AnonymousObservable, ObservableBase
from rx.internal.basic import default_sub_comparer

def extrema_by(source, key_mapper, comparer):
    def subscribe(observer, scheduler=None):
        has_value = [False]
        last_key = [None]
        list = []

        def on_next(x):
            try:
                key = key_mapper(x)
            except Exception as ex:
                observer.on_error(ex)
                return

            comparison = 0;

            if not has_value[0]:
                has_value[0] = True
                last_key[0] = key
            else:
                try:
                    comparison = comparer(key, last_key[0])
                except Exception as ex1:
                    observer.on_error(ex1)
                    return

            if comparison > 0:
                last_key[0] = key
                #list.clear()
                list[:] = []

            if comparison >= 0:
                list.append(x)

        def on_completed():
            observer.on_next(list)
            observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
    return AnonymousObservable(subscribe)


def min_by(source, key_mapper, comparer=None) -> ObservableBase:
    """Returns the elements in an observable sequence with the minimum key
    value according to the specified comparer.

    Example
    res = source.min_by(lambda x: x.value)
    res = source.min_by(lambda x: x.value, lambda x, y: x - y)

    Keyword arguments:
    key_mapper -- {Function} Key mapper function.
    comparer -- {Function} [Optional] Comparer used to compare key values.

    Returns an observable {Observable} sequence containing a list of zero
    or more elements that have a minimum key value.
    """

    comparer = comparer or default_sub_comparer

    return extrema_by(source, key_mapper, lambda x, y: comparer(x, y) * -1)
