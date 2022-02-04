from typing import Callable, List, Optional, TypeVar, Iterable

import rx
from rx.core import Observable, typing, abc
from rx.disposable import CompositeDisposable
from rx.internal import default_comparer

_T = TypeVar("_T")


def _sequence_equal(
    second: Observable[_T], comparer: Optional[typing.Comparer[_T]] = None
) -> Callable[[Observable[_T]], Observable[bool]]:
    comparer = comparer or default_comparer
    if isinstance(second, Iterable):
        second = rx.from_iterable(second)

    def sequence_equal(source: Observable[_T]) -> Observable[bool]:
        """Determines whether two sequences are equal by comparing the
        elements pairwise using a specified equality comparer.

        Examples:
            >>> res = sequence_equal([1,2,3])
            >>> res = sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
            >>> res = sequence_equal(rx.return_value(42))
            >>> res = sequence_equal(rx.return_value({ "value": 42 }), lambda x, y: x.value == y.value)

        Args:
            source: Source obserable to compare.

        Returns:
            An observable sequence that contains a single element which
        indicates whether both sequences are of equal length and their
        corresponding elements are equal according to the specified
        equality comparer.
        """
        first = source

        def subscribe(
            observer: abc.ObserverBase[bool],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            donel = [False]
            doner = [False]
            ql: List[_T] = []
            qr: List[_T] = []

            def on_next1(x: _T) -> None:
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

            def on_completed1() -> None:
                donel[0] = True
                if not ql:
                    if qr:
                        observer.on_next(False)
                        observer.on_completed()
                    elif doner[0]:
                        observer.on_next(True)
                        observer.on_completed()

            def on_next2(x: _T):
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
                if not qr:
                    if len(ql) > 0:
                        observer.on_next(False)
                        observer.on_completed()
                    elif donel[0]:
                        observer.on_next(True)
                        observer.on_completed()

            subscription1 = first.subscribe_(
                on_next1, observer.on_error, on_completed1, scheduler
            )
            subscription2 = second.subscribe_(
                on_next2, observer.on_error, on_completed2, scheduler
            )
            return CompositeDisposable(subscription1, subscription2)

        return Observable(subscribe)

    return sequence_equal


__all__ = ["_sequence_equal"]
