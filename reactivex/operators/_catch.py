from asyncio import Future
from typing import Callable, Optional, TypeVar, Union

import reactivex
from reactivex import Observable, abc
from reactivex.disposable import SerialDisposable, SingleAssignmentDisposable

_T = TypeVar("_T")


def catch_handler(
    source: Observable[_T],
    handler: Callable[[Exception, Observable[_T]], Union[Observable[_T], "Future[_T]"]],
) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        d1 = SingleAssignmentDisposable()
        subscription = SerialDisposable()

        subscription.disposable = d1

        def on_error(exception: Exception) -> None:
            try:
                result = handler(exception, source)
            except Exception as ex:  # By design. pylint: disable=W0703
                observer.on_error(ex)
                return

            result = (
                reactivex.from_future(result) if isinstance(result, Future) else result
            )
            d = SingleAssignmentDisposable()
            subscription.disposable = d
            d.disposable = result.subscribe(observer, scheduler=scheduler)

        d1.disposable = source.subscribe(
            observer.on_next, on_error, observer.on_completed, scheduler=scheduler
        )
        return subscription

    return Observable(subscribe)


def catch_(
    handler: Union[
        Observable[_T], Callable[[Exception, Observable[_T]], Observable[_T]]
    ]
) -> Callable[[Observable[_T]], Observable[_T]]:
    def catch(source: Observable[_T]) -> Observable[_T]:
        """Continues an observable sequence that is terminated by an
        exception with the next observable sequence.

        Examples:
            >>> op = catch(ys)
            >>> op = catch(lambda ex, src: ys(ex))

        Args:
            handler: Second observable sequence used to produce
                results when an error occurred in the first sequence, or an
                exception handler function that returns an observable sequence
                given the error and source observable that occurred in the
                first sequence.

        Returns:
            An observable sequence containing the first sequence's
            elements, followed by the elements of the handler sequence
            in case an exception occurred.
        """
        if callable(handler):
            return catch_handler(source, handler)
        else:
            return reactivex.catch(source, handler)

    return catch


__all__ = ["catch_"]
