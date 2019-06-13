from typing import Optional

from rx.core import Observable, typing
from rx.internal.exceptions import ArgumentOutOfRangeException


def _element_at_or_default(index, has_default=False, default_value=None):
    if index < 0:
        raise ArgumentOutOfRangeException()

    def element_at_or_default(source: Observable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
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

            return source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return element_at_or_default
