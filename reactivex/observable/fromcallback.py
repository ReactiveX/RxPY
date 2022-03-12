from typing import Any, Callable, Optional

from reactivex import Observable, abc, typing
from reactivex.disposable import Disposable


def from_callback_(
    func: Callable[..., Callable[..., None]],
    mapper: Optional[typing.Mapper[Any, Any]] = None,
) -> Callable[[], Observable[Any]]:
    """Converts a callback function to an observable sequence.

    Args:
        func: Function with a callback as the last argument to
            convert to an Observable sequence.
        mapper: [Optional] A mapper which takes the arguments
            from the callback to produce a single item to yield on next.

    Returns:
        A function, when executed with the required arguments minus
        the callback, produces an Observable sequence with a single value of
        the arguments to the callback as a list.
    """

    def function(*args: Any) -> Observable[Any]:
        arguments = list(args)

        def subscribe(
            observer: abc.ObserverBase[Any],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            def handler(*args: Any) -> None:
                results = list(args)
                if mapper:
                    try:
                        results = mapper(args)
                    except Exception as err:  # pylint: disable=broad-except
                        observer.on_error(err)
                        return

                    observer.on_next(results)
                else:
                    if len(results) <= 1:
                        observer.on_next(*results)
                    else:
                        observer.on_next(results)

                    observer.on_completed()

            arguments.append(handler)
            func(*arguments)
            return Disposable()

        return Observable(subscribe)

    return function


__all__ = ["from_callback_"]
