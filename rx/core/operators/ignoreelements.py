from typing import Callable, Optional

from rx.core import Observable, typing
from rx.internal import noop


def _ignore_elements() -> Callable[[Observable], Observable]:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns:
        An empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
    """

    def ignore_elements(source: Observable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            return source.subscribe(
                noop,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )

        return Observable(subscribe_observer=subscribe_observer)
    return ignore_elements
