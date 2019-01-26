from typing import Any, Callable
from rx.core import Observable
from rx.internal.exceptions import ArgumentOutOfRangeException


def _element_at_or_default(index, has_default=False, default_value=None):
    if index < 0:
        raise ArgumentOutOfRangeException()

    def element_at_or_default(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            i = [index]

            def on_next(x):
                found = False
                with source.lock:
                    if i[0]:
                        i[0] -= 1
                    else:
                        found = True

                if found:
                    observer.on_next(x)
                    observer.on_completed()

            def on_completed():
                if not has_default:
                    observer.on_error(ArgumentOutOfRangeException())
                else:
                    observer.on_next(default_value)
                    observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return element_at_or_default
