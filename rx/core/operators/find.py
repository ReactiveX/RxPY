from typing import Callable
from rx.core import Observable
from rx.core.typing import Predicate


def _find_value(predicate: Predicate, yield_index) -> Callable[[Observable], Observable]:
    def find_value(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            i = [0]

            def on_next(x):
                should_run = False
                try:
                    should_run = predicate(x, i, source)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(i[0] if yield_index else x)
                    observer.on_completed()
                else:
                    i[0] += 1

            def on_completed():
                observer.on_next(-1 if yield_index else None)
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return find_value
