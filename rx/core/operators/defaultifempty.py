from typing import Any, Callable, Optional

from rx.core import Observable, typing


def _default_if_empty(default_value: Any = None) -> Callable[[Observable], Observable]:
    def default_if_empty(source: Observable) -> Observable:
        """Returns the elements of the specified sequence or the
        specified value in a singleton sequence if the sequence is
        empty.

        Examples:
            >>> obs = default_if_empty(source)

        Args:
            source: Source observable.

        Returns:
            An observable sequence that contains the specified default
            value if the source is empty otherwise, the elements of the
            source.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            found = [False]

            def on_next(x: Any):
                found[0] = True
                observer.on_next(x)

            def on_completed():
                if not found[0]:
                    observer.on_next(default_value)
                observer.on_completed()

            return source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return default_if_empty
