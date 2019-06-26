from typing import Iterable

from rx.disposable import Disposable
from rx.core import Observable
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable, SerialDisposable
from rx.scheduler import CurrentThreadScheduler


def _catch_with_iterable(sources: Iterable[Observable]) -> Observable:

    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> res = catch([xs, ys, zs])
        >>> res = rx.catch(src for src in [xs, ys, zs])

    Args:
        sources: an Iterable of observables. Thus a generator is accepted.

    Returns:
        An observable sequence containing elements from consecutive
        source sequences until a source sequence terminates
        successfully.
    """

    sources_ = iter(sources)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or CurrentThreadScheduler.singleton()

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        last_exception = [None]
        is_disposed = []

        def action(action1, state=None):
            def on_error(exn):
                last_exception[0] = exn
                cancelable.disposable = scheduler.schedule(action)

            if is_disposed:
                return

            try:
                current = next(sources_)
            except StopIteration:
                if last_exception[0]:
                    observer.on_error(last_exception[0])
                else:
                    observer.on_completed()
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe_(observer.on_next, on_error, observer.on_completed, scheduler)

        cancelable.disposable = scheduler.schedule(action)

        def dispose():
            is_disposed.append(True)
        return CompositeDisposable(subscription, cancelable, Disposable(dispose))
    return Observable(subscribe)
