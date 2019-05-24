from typing import Optional

from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable


def _combine_latest(*sources: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the
    observable sequences produces an element.

    Examples:
        >>> obs = combine_latest(obs1, obs2, obs3)

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.
    """

    parent = sources[0]

    def subscribe(observer: typing.Observer,
                  scheduler: Optional[typing.Scheduler] = None
                  ) -> CompositeDisposable:

        n = len(sources)
        has_value = [False] * n
        has_value_all = [False]
        is_done = [False] * n
        values = [None] * n

        def _next(i):
            has_value[i] = True

            if has_value_all[0] or all(has_value):
                res = tuple(values)
                observer.on_next(res)

            elif all([x for j, x in enumerate(is_done) if j != i]):
                observer.on_completed()

            has_value_all[0] = all(has_value)

        def done(i):
            is_done[i] = True
            if all(is_done):
                observer.on_completed()

        subscriptions = [None] * n

        def func(i):
            subscriptions[i] = SingleAssignmentDisposable()

            def on_next(x):
                with parent.lock:
                    values[i] = x
                    _next(i)

            def on_completed():
                with parent.lock:
                    done(i)

            subscriptions[i].disposable = sources[i].subscribe_(on_next, observer.on_error, on_completed, scheduler)

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return Observable(subscribe)
