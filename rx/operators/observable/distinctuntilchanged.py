from rx.core import ObservableBase, AnonymousObservable
from rx.internal.basic import identity, default_comparer


def distinct_until_changed(self, key_mapper=None, comparer=None) -> ObservableBase:
    """Returns an observable sequence that contains only distinct
    contiguous elements according to the key_mapper and the comparer.

    1 - obs = observable.distinct_until_changed();
    2 - obs = observable.distinct_until_changed(lambda x: x.id)
    3 - obs = observable.distinct_until_changed(lambda x: x.id,
                                                lambda x, y: x == y)

    key_mapper -- [Optional] A function to compute the comparison key
        for each element. If not provided, it projects the value.
    comparer -- [Optional] Equality comparer for computed key values. If
        not provided, defaults to an equality comparer function.

    Return an observable sequence only containing the distinct
    contiguous elements, based on a computed key value, from the source
    sequence.
    """

    source = self
    key_mapper = key_mapper or identity
    comparer = comparer or default_comparer

    def subscribe(observer, scheduler=None):
        has_current_key = [False]
        current_key = [None]

        def send(value):
            comparer_equals = False
            try:
                key = key_mapper(value)
            except Exception as exception:
                observer.throw(exception)
                return

            if has_current_key[0]:
                try:
                    comparer_equals = comparer(current_key[0], key)
                except Exception as exception:
                    observer.throw(exception)
                    return

            if not has_current_key[0] or not comparer_equals:
                has_current_key[0] = True
                current_key[0] = key
                observer.send(value)

        return source.subscribe_(send, observer.throw, observer.close)
    return AnonymousObservable(subscribe)
