from typing import Callable, Optional, Tuple, TypeVar, cast

from reactivex import Observable, abc

_T = TypeVar("_T")


def pairwise_() -> Callable[[Observable[_T]], Observable[Tuple[_T, _T]]]:
    def pairwise(source: Observable[_T]) -> Observable[Tuple[_T, _T]]:
        """Partially applied pairwise operator.

        Returns a new observable that triggers on the second and
        subsequent triggerings of the input observable. The Nth
        triggering of the input observable passes the arguments from
        the N-1th and Nth triggering as a pair. The argument passed to
        the N-1th triggering is held in hidden internal state until the
        Nth triggering occurs.

        Returns:
            An observable that triggers on successive pairs of
            observations from the input observable as an array.
        """

        def subscribe(
            observer: abc.ObserverBase[Tuple[_T, _T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            has_previous = False
            previous: _T = cast(_T, None)

            def on_next(x: _T) -> None:
                nonlocal has_previous, previous
                pair = None

                with source.lock:
                    if has_previous:
                        pair = (previous, x)
                    else:
                        has_previous = True

                    previous = x

                if pair:
                    observer.on_next(pair)

            return source.subscribe(on_next, observer.on_error, observer.on_completed)

        return Observable(subscribe)

    return pairwise


__all__ = ["pairwise_"]
