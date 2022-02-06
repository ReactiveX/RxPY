from typing import Callable, Optional

from rx.core import Observable, abc
from rx.core.typing import Mapper
from rx.disposable import Disposable


def _from_callback(
    func: Callable, mapper: Optional[Mapper] = None
) -> Callable[[], Observable]:
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

    def function(*args):
        arguments = list(args)

        def subscribe(
            observer: abc.ObserverBase, scheduler: Optional[abc.SchedulerBase] = None
        ) -> abc.DisposableBase:
            def handler(*args):
                results = list(args)
                if mapper:
                    try:
                        results = mapper(args)
                    except Exception as err:  # pylint: disable=broad-except
                        observer.on_error(err)
                        return

                    observer.on_next(results)
                else:
                    if isinstance(results, list) and len(results) <= 1:
                        observer.on_next(*results)
                    else:
                        observer.on_next(results)

                    observer.on_completed()

            arguments.append(handler)
            func(*arguments)
            return Disposable()

        return Observable(subscribe)

    return function
