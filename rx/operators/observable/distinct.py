from rx.core import ObservableBase, AnonymousObservable
from rx.internal.basic import identity, default_comparer

# Swap out for Array.findIndex
def array_index_of_comparer(array, item, comparer):
    for i, a in enumerate(array):
        if comparer(a, item):
            return i
    return -1

class HashSet(object):
    def __init__(self, comparer):
        self.comparer = comparer
        self.set = []

    def push(self, value):
        ret_value = array_index_of_comparer(self.set, value, self.comparer) == -1
        ret_value and self.set.append(value)
        return ret_value


def distinct(self, key_mapper=None, comparer=None) -> ObservableBase:
    """Returns an observable sequence that contains only distinct
    elements according to the key_mapper and the comparer. Usage of
    this operator should be considered carefully due to the maintenance
    of an internal lookup structure which can grow large.

    Example:
    res = obs = xs.distinct()
    obs = xs.distinct(lambda x: x.id)
    obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)

    Keyword arguments:
    key_mapper -- [Optional]  A function to compute the comparison key
        for each element.
    comparer -- [Optional]  Used to compare items in the collection.

    Returns an observable sequence only containing the distinct
    elements, based on a computed key value, from the source sequence.
    """

    source = self
    comparer = comparer or default_comparer

    def subscribe(observer, scheduler=None):
        hashset = HashSet(comparer)

        def send(x):
            key = x

            if key_mapper:
                try:
                    key = key_mapper(x)
                except Exception as ex:
                    observer.throw(ex)
                    return

            hashset.push(key) and observer.send(x)
        return source.subscribe_callbacks(send, observer.throw,
                                observer.close, scheduler)
    return AnonymousObservable(subscribe)
