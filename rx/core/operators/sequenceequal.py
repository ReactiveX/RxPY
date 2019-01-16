from typing import Any, Callable
import collections

from rx.core import AnonymousObservable, ObservableBase, Observable
from rx.disposables import CompositeDisposable
from rx.internal import default_comparer


def sequence_equal(source, second: ObservableBase,
                   comparer: Callable[[Any, Any], bool] = None) -> ObservableBase:
    """Determines whether two sequences are equal by comparing the
    elements pairwise using a specified equality comparer.

    1 - res = source.sequence_equal([1,2,3])
    2 - res = source.sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
    3 - res = source.sequence_equal(rx.return_value(42))
    4 - res = source.sequence_equal(rx.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

    second -- Second observable sequence or array to compare.
    comparer -- [Optional] Comparer used to compare elements of both
        sequences. No guarantees on order of comparer arguments.

    Returns an observable sequence that contains a single element which
    indicates whether both sequences are of equal length and their
    corresponding elements are equal according to the specified equality
    comparer.
    """

    first = source
    comparer = comparer or default_comparer

    if isinstance(second, collections.abc.Iterable):
        second = Observable.from_iterable(second)

    def subscribe(observer, scheduler=None):
        donel = [False]
        doner = [False]
        ql = []
        qr = []

        def on_next1(x):
            if len(qr) > 0:
                v = qr.pop(0)
                try:
                    equal = comparer(v, x)
                except Exception as e:
                    observer.on_error(e)
                    return

                if not equal:
                    observer.on_next(False)
                    observer.on_completed()

            elif doner[0]:
                observer.on_next(False)
                observer.on_completed()
            else:
                ql.append(x)

        def on_completed1():
            donel[0] = True
            if not len(ql):
                if len(qr) > 0:
                    observer.on_next(False)
                    observer.on_completed()
                elif doner[0]:
                    observer.on_next(True)
                    observer.on_completed()

        def on_next2(x):
            if len(ql) > 0:
                v = ql.pop(0)
                try:
                    equal = comparer(v, x)
                except Exception as exception:
                    observer.on_error(exception)
                    return

                if not equal:
                    observer.on_next(False)
                    observer.on_completed()

            elif donel[0]:
                observer.on_next(False)
                observer.on_completed()
            else:
                qr.append(x)

        def on_completed2():
            doner[0] = True
            if not len(qr):
                if len(ql) > 0:
                    observer.on_next(False)
                    observer.on_completed()
                elif donel[0]:
                    observer.on_next(True)
                    observer.on_completed()

        subscription1 = first.subscribe_(on_next1, observer.on_error, on_completed1, scheduler)
        subscription2 = second.subscribe_(on_next2, observer.on_error, on_completed2, scheduler)
        return CompositeDisposable(subscription1, subscription2)
    return AnonymousObservable(subscribe)
