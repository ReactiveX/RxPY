from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable


def _amb(left_source, right_source):
    """Propagates the observable sequence that reacts first.

    right_source Second observable sequence.

    returns an observable sequence that surfaces either of the given
    sequences, whichever reacted first.
    """

    right_source = Observable.from_future(right_source)

    def subscribe(observer, scheduler=None):
        choice = [None]
        left_choice = 'L'
        right_choice = 'R',
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

        def send_left(value):
            with left_source.lock:
                choice_left()
            if choice[0] == left_choice:
                observer.send(value)

        def throw_left(err):
            with left_source.lock:
                choice_left()
            if choice[0] == left_choice:
                observer.throw(err)

        def close_left():
            with left_source.lock:
                choice_left()
            if choice[0] == left_choice:
                observer.close()

        lelf_d = left_source.subscribe_(send_left, throw_left, close_left, scheduler)
        left_subscription.disposable = lelf_d

        def send_right(value):
            with left_source.lock:
                choice_right()
            if choice[0] == right_choice:
                observer.send(value)

        def throw_right(err):
            with left_source.lock:
                choice_right()
            if choice[0] == right_choice:
                observer.throw(err)

        def close_right():
            with left_source.lock:
                choice_right()
            if choice[0] == right_choice:
                observer.close()

        right_d = right_source.subscribe_(send_right, throw_right, close_right, scheduler)
        right_subscription.disposable = right_d
        return CompositeDisposable(left_subscription, right_subscription)
    return AnonymousObservable(subscribe)


def amb(*args):
    """Propagates the observable sequence that reacts first.

    E.g. winner = Observable.amb(xs, ys, zs)

    Returns an observable sequence that surfaces any of the given
    sequences, whichever reacted first.
    """

    acc = Observable.never()
    if isinstance(args[0], list):
        items = args[0]
    else:
        items = list(args)

    def func(previous, current):
        return _amb(previous, current)

    for item in items:
        acc = func(acc, item)

    return acc
