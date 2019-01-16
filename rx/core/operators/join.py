from typing import Callable
from collections import OrderedDict

from rx.core import AnonymousObservable, Observable
from rx.internal import noop
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable


def _join(right, left_duration_mapper, right_duration_mapper, result_mapper) -> Callable[[Observable], Observable]:
    def join(source: Observable) -> Observable:
        """Correlates the elements of two sequences based on
        overlapping durations.

        Args:
            source: Source observable.

        Return:
            An observable sequence that contains result elements
            computed from source elements that have an overlapping
            duration.
        """

        left = source

        def subscribe(observer, scheduler=None):
            group = CompositeDisposable()
            left_done = [False]
            left_map = OrderedDict()
            left_id = [0]
            right_done = [False]
            right_map = OrderedDict()
            right_id = [0]

            def on_next_left(value):
                duration = None
                current_id = left_id[0]
                left_id[0] += 1
                md = SingleAssignmentDisposable()

                left_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in left_map:
                        del left_map[current_id]
                    if not len(left_map) and left_done[0]:
                        observer.on_completed()

                    return group.remove(md)

                try:
                    duration = left_duration_mapper(value)
                except Exception as exception:
                    observer.on_error(exception)
                    return

                md.disposable = duration.take(1).subscribe_(noop, observer.on_error, lambda: expire(), scheduler)

                for val in right_map.values():
                    try:
                        result = result_mapper(value, val)
                    except Exception as exception:
                        observer.on_error(exception)
                        return

                    observer.on_next(result)

            def on_completed_left():
                left_done[0] = True
                if right_done[0] or not len(left_map):
                    observer.on_completed()

            group.add(left.subscribe_(on_next_left, observer.on_error, on_completed_left, scheduler))

            def on_next_right(value):
                duration = None
                current_id = right_id[0]
                right_id[0] += 1
                md = SingleAssignmentDisposable()
                right_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in right_map:
                        del right_map[current_id]
                    if not len(right_map) and right_done[0]:
                        observer.on_completed()

                    return group.remove(md)

                try:
                    duration = right_duration_mapper(value)
                except Exception as exception:
                    observer.on_error(exception)
                    return

                md.disposable = duration.take(1).subscribe_(noop, observer.on_error, lambda: expire(), scheduler)

                for val in left_map.values():
                    try:
                        result = result_mapper(val, value)
                    except Exception as exception:
                        observer.on_error(exception)
                        return

                    observer.on_next(result)

            def on_completed_right():
                right_done[0] = True
                if left_done[0] or not len(right_map):
                    observer.on_completed()

            group.add(right.subscribe_(on_next_right, observer.on_error, on_completed_right))
            return group
        return AnonymousObservable(subscribe)
    return join
