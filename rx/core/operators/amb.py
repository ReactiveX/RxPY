from asyncio import Future
from typing import cast, Any, Union

from rx import from_future
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future


def _amb(right_source: Observable):

    if is_future(right_source):
        obs = from_future(cast(Future, right_source))
    else:
        obs = cast(Observable, right_source)

    def amb(left_source: Observable):
        def subscribe(observer: typing.Observer, scheduler: typing.Scheduler = None) -> typing.Disposable:
            choice = [None]
            left_choice = 'L'
            right_choice = 'R'
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

            def on_next_left(value):
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_next(value)

            def on_error_left(err):
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_error(err)

            def on_completed_left():
                with left_source.lock:
                    choice_left()
                if choice[0] == left_choice:
                    observer.on_completed()

            left_d = left_source.subscribe_(on_next_left, on_error_left, on_completed_left, scheduler)
            left_subscription.disposable = left_d

            def send_right(value: Any) -> None:
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

            right_d = obs.subscribe_(send_right, on_error_right, on_completed_right, scheduler)
            right_subscription.disposable = right_d
            return CompositeDisposable(left_subscription, right_subscription)
        return Observable(subscribe)
    return amb