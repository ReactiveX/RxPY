from typing import Callable
from rx.core import Observable


def _skip_last(count: int) -> Callable[[Observable], Observable]:
    def skip_last(source: Observable) -> Observable:
        """Bypasses a specified number of elements at the end of an
        observable sequence.

        This operator accumulates a queue with a length enough to store
        the first `count` elements. As more elements are received,
        elements are taken from the front of the queue and produced on
        the result sequence. This causes elements to be delayed.

        Args:
            count: Number of elements to bypass at the end of the
            source sequence.

        Returns:
            An observable sequence containing the source sequence
            elements except for the bypassed ones at the end.
        """

        def subscribe(observer, scheduler=None):
            q = []

            def on_next(value):
                front = None
                with source.lock:
                    q.append(value)
                    if len(q) > count:
                        front = q.pop(0)

                if front is not None:
                    observer.on_next(front)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return Observable(subscribe)
    return skip_last
