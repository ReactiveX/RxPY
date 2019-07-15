from typing import Any, Callable

from rx import defer, from_future, of
from rx.core import Observable
from rx.core.typing import Accumulator
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.concurrency import synchronized
from rx.internal.utils import NotSet, is_future


def _merge_scan(accumulator: Accumulator, seed: Any = NotSet) -> Callable[[Observable], Observable]:

    def merge_scan(source: Observable) -> Observable:
        """Partially applied merge_scan operator.

        Applies an accumulator function, which returns an observable sequence,
        over an observable sequence and returns each intermediate result.

        Examples:
            >>> scanned = merge_scan(source)

        Args:
            source: The observable source to scan.

        Returns:
            An observable sequence containing the accumulated values.
        """
        def subscribe(observer, scheduler=None):
            accumulator_value = [seed]
            active = [False]
            group = CompositeDisposable()
            is_stopped = [False]
            queue = []

            def subscribe(xs):
                subscription = SingleAssignmentDisposable()
                group.add(subscription)

                @synchronized(source.lock)
                def on_next(next_accumulator_value):
                    accumulator_value[0] = next_accumulator_value
                    observer.on_next(next_accumulator_value)

                @synchronized(source.lock)
                def on_completed():
                    group.remove(subscription)
                    if queue:
                        s = queue.pop(0)
                        subscribe(s)
                    else:
                        active[0] = False
                        if is_stopped[0]:
                            observer.on_completed()

                on_error = synchronized(source.lock)(observer.on_error)
                subscription.disposable = xs.subscribe_(on_next, on_error, on_completed, scheduler)

            def on_next(value):
                def accumulate():
                    has_accumulator_value = accumulator_value[0] is not NotSet
                    if has_accumulator_value:
                        acc_source = accumulator(accumulator_value[0], value)
                        return from_future(acc_source) if is_future(acc_source) else acc_source
                    else:
                        return of(value)

                accumulator_source = defer(lambda _: accumulate())
                if not active[0]:
                    active[0] = True
                    subscribe(accumulator_source)
                else:
                    queue.append(accumulator_source)

            def on_completed():
                is_stopped[0] = True
                if not active[0]:
                    observer.on_completed()

            group.add(source.subscribe_(on_next, observer.on_error, on_completed, scheduler))
            return group
        return Observable(subscribe)
    return merge_scan

