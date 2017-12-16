import collections

from rx.core import AnonymousObservable, Observable
from rx.disposables import CompositeDisposable
from rx.internal import default_comparer
from rx.internal import extensionmethod


@extensionmethod(Observable)
def sequence_equal(self, second, comparer=None):
    """Determines whether two sequences are equal by comparing the
    elements pairwise using a specified equality comparer.

    1 - res = source.sequence_equal([1,2,3])
    2 - res = source.sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
    3 - res = source.sequence_equal(Observable.return_value(42))
    4 - res = source.sequence_equal(Observable.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

    second -- Second observable sequence or array to compare.
    comparer -- [Optional] Comparer used to compare elements of both sequences.
                No guarantees on order of comparer arguments.

    Returns an observable sequence that contains a single element which
    indicates whether both sequences are of equal length and their
    corresponding elements are equal according to the specified equality
    comparer.
    """

    first = self
    comparer = comparer or default_comparer

    if isinstance(second, collections.Iterable):
        second = Observable.from_iterable(second)

    def subscribe(observer, scheduler=None):
        donel = [False]
        doner = [False]
        ql = []
        qr = []

        def send1(x):
            if len(qr) > 0:
                v = qr.pop(0)
                try:
                    equal = comparer(v, x)
                except Exception as e:
                    observer.throw(e)
                    return

                if not equal:
                    observer.send(False)
                    observer.close()

            elif doner[0]:
                observer.send(False)
                observer.close()
            else:
                ql.append(x)

        def close1():
            donel[0] = True
            if not len(ql):
                if len(qr) > 0:
                    observer.send(False)
                    observer.close()
                elif doner[0]:
                    observer.send(True)
                    observer.close()

        def send2(x):
            if len(ql) > 0:
                v = ql.pop(0)
                try:
                    equal = comparer(v, x)
                except Exception as exception:
                    observer.throw(exception)
                    return

                if not equal:
                    observer.send(False)
                    observer.close()

            elif donel[0]:
                observer.send(False)
                observer.close()
            else:
                qr.append(x)

        def close2():
            doner[0] = True
            if not len(qr):
                if len(ql) > 0:
                    observer.send(False)
                    observer.close()
                elif donel[0]:
                    observer.send(True)
                    observer.close()

        subscription1 = first.subscribe_callbacks(send1, observer.throw, close1)
        subscription2 = second.subscribe_callbacks(send2, observer.throw, close2)
        return CompositeDisposable(subscription1, subscription2)
    return AnonymousObservable(subscribe)
