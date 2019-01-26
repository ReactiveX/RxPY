from typing import Callable

from rx.core import Observable


def _pairwise() -> Callable[[Observable], Observable]:
    def pairwise(source: Observable) -> Observable:
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

        def subscribe(observer, scheduler=None):
            has_previous = [False]
            previous = [None]

            def on_next(x):
                pair = None

                with source.lock:
                    if has_previous[0]:
                        pair = (previous[0], x)
                    else:
                        has_previous[0] = True

                    previous[0] = x

                if pair:
                    observer.on_next(pair)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed)
        return Observable(subscribe)
    return pairwise
