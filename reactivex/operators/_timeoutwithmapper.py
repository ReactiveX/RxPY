from typing import Any, Callable, Optional, TypeVar

import reactivex
from reactivex import Observable, abc
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)

_T = TypeVar("_T")


def timeout_with_mapper_(
    first_timeout: Optional[Observable[_T]] = None,
    timeout_duration_mapper: Optional[Callable[[Any], Observable[Any]]] = None,
    other: Optional[Observable[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the source observable sequence, switching to the other
    observable sequence if a timeout is signaled.

        res = timeout_with_mapper(reactivex.timer(500))
        res = timeout_with_mapper(reactivex.timer(500), lambda x: reactivex.timer(200))
        res = timeout_with_mapper(
            reactivex.timer(500),
            lambda x: reactivex.timer(200)),
            reactivex.return_value(42)
        )

    Args:
        first_timeout -- [Optional] Observable sequence that represents the
            timeout for the first element. If not provided, this defaults to
            reactivex.never().
        timeout_duration_mapper -- [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the
            current element and the next element.
        other -- [Optional] Sequence to return in case of a timeout. If not
            provided, this is set to reactivex.throw().

    Returns:
        The source sequence switching to the other sequence in case
    of a timeout.
    """

    first_timeout_ = first_timeout or reactivex.never()
    other_ = other or reactivex.throw(Exception("Timeout"))

    def timeout_with_mapper(source: Observable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            subscription = SerialDisposable()
            timer = SerialDisposable()
            original = SingleAssignmentDisposable()

            subscription.disposable = original

            switched = False
            _id = [0]

            def set_timer(timeout: Observable[Any]) -> None:
                my_id = _id[0]

                def timer_wins():
                    return _id[0] == my_id

                d = SingleAssignmentDisposable()
                timer.disposable = d

                def on_next(x: Any) -> None:
                    if timer_wins():
                        subscription.disposable = other_.subscribe(
                            observer, scheduler=scheduler
                        )

                    d.dispose()

                def on_error(e: Exception) -> None:
                    if timer_wins():
                        observer.on_error(e)

                def on_completed() -> None:
                    if timer_wins():
                        subscription.disposable = other_.subscribe(observer)

                d.disposable = timeout.subscribe(
                    on_next, on_error, on_completed, scheduler=scheduler
                )

            set_timer(first_timeout_)

            def observer_wins():
                res = not switched
                if res:
                    _id[0] += 1

                return res

            def on_next(x: _T) -> None:
                if observer_wins():
                    observer.on_next(x)
                    timeout = None
                    try:
                        timeout = (
                            timeout_duration_mapper(x)
                            if timeout_duration_mapper
                            else reactivex.never()
                        )
                    except Exception as e:
                        observer.on_error(e)
                        return

                    set_timer(timeout)

            def on_error(error: Exception) -> None:
                if observer_wins():
                    observer.on_error(error)

            def on_completed() -> None:
                if observer_wins():
                    observer.on_completed()

            original.disposable = source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            return CompositeDisposable(subscription, timer)

        return Observable(subscribe)

    return timeout_with_mapper


__all__ = ["timeout_with_mapper_"]
