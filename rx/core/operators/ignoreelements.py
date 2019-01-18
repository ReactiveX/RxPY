from rx.core import Observable, AnonymousObservable
from rx.internal import noop


def _ignore_elements() -> Observable:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns:
        An empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
    """

    def ignore_elements(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            return source.subscribe_(noop, observer.on_error, observer.on_completed, scheduler)

        return AnonymousObservable(subscribe)
    return ignore_elements