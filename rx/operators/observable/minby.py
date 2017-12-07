from rx import AnonymousObservable, Observable
from rx.internal.basic import default_sub_comparer
from rx.internal import extensionmethod

def extrema_by(source, key_selector, comparer):
    def subscribe(observer, scheduler=None):
        has_value = [False]
        last_key = [None]
        list = []

        def send(x):
            try:
                key = key_selector(x)
            except Exception as ex:
                observer.throw(ex)
                return

            comparison = 0;

            if not has_value[0]:
                has_value[0] = True
                last_key[0] = key
            else:
                try:
                    comparison = comparer(key, last_key[0])
                except Exception as ex1:
                    observer.throw(ex1)
                    return

            if comparison > 0:
                last_key[0] = key
                #list.clear()
                list[:] = []

            if comparison >= 0:
                list.append(x)

        def close():
            observer.send(list)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def min_by(self, key_selector, comparer=None):
    """Returns the elements in an observable sequence with the minimum key
    value according to the specified comparer.

    Example
    res = source.min_by(lambda x: x.value)
    res = source.min_by(lambda x: x.value, lambda x, y: x - y)

    Keyword arguments:
    key_selector -- {Function} Key selector function.
    comparer -- {Function} [Optional] Comparer used to compare key values.

    Returns an observable {Observable} sequence containing a list of zero
    or more elements that have a minimum key value.
    """

    comparer = comparer or default_sub_comparer

    return extrema_by(self, key_selector, lambda x, y: comparer(x, y) * -1)

