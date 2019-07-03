from contextlib import contextmanager

from typing import Callable, Optional
from rx.core import Observable
from rx.core.typing import Mapper, Comparer
from rx.disposable import CompositeDisposable
from rx.internal.basic import default_comparer


def array_index_of_comparer(array, item, comparer):
    for i, a in enumerate(array):
        if comparer(a, item):
            return i
    return -1


@contextmanager
def nullcontext():
    """For Python 3.6 compatibility
    """
    yield


class HashSet:
    def __init__(self, comparer, lock=None):
        self.comparer = comparer
        self.set = []
        self.lock = lock

    def push(self, value):
        with self.lock or nullcontext():
            ret_value = array_index_of_comparer(self.set, value, self.comparer) == -1
            if ret_value:
                self.set.append(value)
            return ret_value

    def flush(self):
        with self.lock or nullcontext():
            self.set = []


def _distinct(key_mapper: Optional[Mapper] = None,
              comparer: Optional[Comparer] = None,
              flushes: Optional[Observable] = None,
              ) -> Callable[[Observable], Observable]:
    comparer = comparer or default_comparer

    def distinct(source: Observable) -> Observable:
        """Returns an observable sequence that contains only distinct
        elements according to the key_mapper and the comparer. Usage of
        this operator should be considered carefully due to the maintenance
        of an internal lookup structure which can grow large.

        Examples:
            >>> res = obs = distinct(source)

        Args:
            source: Source observable to return distinct items from.

        Returns:
            An observable sequence only containing the distinct
            elements, based on a computed key value, from the source
            sequence.
        """

        def subscribe(observer, scheduler=None):
            hashset = HashSet(comparer, lock=flushes.lock if flushes else None)

            def on_next(x):
                key = x

                if key_mapper:
                    try:
                        key = key_mapper(x)
                    except Exception as ex:
                        observer.on_error(ex)
                        return

                hashset.push(key) and observer.on_next(x)

            source_disposable = source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)

            if flushes:
                flushes_disposable = flushes.subscribe_(lambda _: hashset.flush(), scheduler=scheduler)
                return CompositeDisposable(source_disposable, flushes_disposable)

            return source_disposable

        return Observable(subscribe)
    return distinct
