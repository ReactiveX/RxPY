from rx import from_future, never
from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future


def amb(right_source):
    right_source = from_future(right_source) if is_future(right_source) else right_source

    def partial(left_source):
        def subscribe(observer, scheduler=None):
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

            lelf_d = left_source.subscribe_(on_next_left, on_error_left, on_completed_left, scheduler)
            left_subscription.disposable = lelf_d

            def send_right(value):
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_next(value)

            def on_error_right(err):
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_error(err)

            def on_completed_right():
                with left_source.lock:
                    choice_right()
                if choice[0] == right_choice:
                    observer.on_completed()

            right_d = right_source.subscribe_(send_right, on_error_right, on_completed_right, scheduler)
            right_subscription.disposable = right_d
            return CompositeDisposable(left_subscription, right_subscription)
        return AnonymousObservable(subscribe)
    return partial


def amb_(*args: Observable):
    """Propagates the observable sequence that reacts first.

    Example:
        >>> winner = amb(xs, ys, zs)

    Returns:
        An observable sequence that surfaces any of the given sequences,
        whichever reacted first.
    """

    acc = never()
    if isinstance(args[0], list):
        items = args[0]
    else:
        items = list(args)

    def func(previous, current):
        return amb(previous)(current)

    for item in items:
        acc = func(acc, item)

    return acc
