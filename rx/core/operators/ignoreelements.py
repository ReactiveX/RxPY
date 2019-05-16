from typing import Callable

from rx.core import Observable
from rx.internal import noop


def _ignore_elements() -> Callable[[Observable], Observable]:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns:
        An empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
    """

    def ignore_elements(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            return source.subscribe_(noop, observer.on_error, observer.on_completed, scheduler)

        return Observable(subscribe)
    return ignore_elements