from typing import Callable

import rx
from rx.core import Observable, AnonymousObservable, typing
from rx.disposable import SingleAssignmentDisposable, SerialDisposable
from rx.internal.utils import is_future


def catch_handler(source, handler) -> Observable:
    def subscribe(observer, scheduler=None):
        d1 = SingleAssignmentDisposable()
        subscription = SerialDisposable()

        subscription.disposable = d1

        def on_error(exception):
            try:
                result = handler(exception)
            except Exception as ex:  # By design. pylint: disable=W0703
                observer.on_error(ex)
                return

            result = rx.from_future(result) if is_future(result) else result
            d = SingleAssignmentDisposable()
            subscription.disposable = d
            d.disposable = result.subscribe(observer, scheduler)

        d1.disposable = source.subscribe_(
            observer.on_next,
            on_error,
            observer.on_completed,
            scheduler
        )
        return subscription
    return AnonymousObservable(subscribe)


def _catch_exception(second: Observable = None, handler=None) -> Callable[[Observable], Observable]:
    def catch_exception(source: Observable) -> Observable:
        """Continues an observable sequence that is terminated by an
        exception with the next observable sequence.

        Examples:
            >>> catch_exception(ys)
            >>> catch_exception(lambda ex: ys(ex))

        Args:
            handler: Exception handler function that returns an
                observable sequence  given the error that occurred in
                the first sequence.
            second: Second observable sequence used to produce
                results when an error occurred in the first sequence.

        Returns:
            An observable sequence containing the first sequence's
            elements, followed by the elements of the handler sequence
            in case an exception occurred.
        """
        if handler or not isinstance(second, typing.Observable):
            return catch_handler(source, handler or second)

        return rx.catch_exception([source, second])
    return catch_exception
