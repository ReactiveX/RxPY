from asyncio import Future
from typing import Callable, List, Optional, TypeVar, Union

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable

_T = TypeVar("_T")


def amb_(
    right_source: Union[Observable[_T], "Future[_T]"]
) -> Callable[[Observable[_T]], Observable[_T]]:

    if isinstance(right_source, Future):
        obs: Observable[_T] = from_future(right_source)
    else:
        obs = right_source

    def amb(left_source: Observable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            choice: List[Optional[str]] = [None]
            left_choice = "L"
            right_choice = "R"
            left_subscription = SingleAssignmentDisposable()
            right_subscription = SingleAssignmentDisposable()

            def choice_left():
                if not choice[0]:
                    choice[0] = left_choice
                    right_subscription.dispose()

            def choice_right():
                if not choice[0]:
                    choice[0] = right_choice
                    left_subscription.dispose()

            def on_next_left(value: _T) -> None:
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_next(value)

            def on_error_left(err: Exception) -> None:
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_error(err)

            def on_completed_left() -> None:
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_completed()

            left_d = left_source.subscribe(
                on_next_left, on_error_left, on_completed_left, scheduler=scheduler
            )
            left_subscription.disposable = left_d

            def send_right(value: _T) -> None:
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_next(value)

            def on_error_right(err: Exception) -> None:
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_error(err)

            def on_completed_right() -> None:
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_completed()

            right_d = obs.subscribe(
                send_right, on_error_right, on_completed_right, scheduler=scheduler
            )
            right_subscription.disposable = right_d
            return CompositeDisposable(left_subscription, right_subscription)

        return Observable(subscribe)

    return amb


__all__ = ["amb_"]
