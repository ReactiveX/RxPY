from typing import Callable, Any
from rx.core import ObservableBase, AnonymousObservable
from rx.core.typing import Mapper


def from_callback(func: Callable, mapper: Mapper = None) -> "Callable[[...], ObservableBase]":
    """Converts a callback function to an observable sequence.

    Keyword arguments:
    func -- Function with a callback as the last parameter to
        convert to an Observable sequence.
    mapper -- [Optional] A mapper which takes the arguments
        from the callback to produce a single item to yield on next.

    Returns a function, when executed with the required parameters minus
    the callback, produces an Observable sequence with a single value of
    the arguments to the callback as a list.
    """

    def function(*args):
        arguments = list(args)

        def subscribe(observer, scheduler=None):
            def handler(*args):
                results = list(args)
                if mapper:
                    try:
                        results = mapper(args)
                    except Exception as err:
                        observer.throw(err)
                        return

                    observer.send(results)
                else:
                    if isinstance(results, list) and len(results) <= 1:
                        observer.send(*results)
                    else:
                        observer.send(results)

                    observer.close()

            arguments.append(handler)
            func(*arguments)

        return AnonymousObservable(subscribe)
    return function
