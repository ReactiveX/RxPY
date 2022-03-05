from collections import OrderedDict
from typing import Any, Callable, Optional, Tuple, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import noop
from reactivex.operators import take

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def join_(
    right: Observable[_T2],
    left_duration_mapper: Callable[[Any], Observable[Any]],
    right_duration_mapper: Callable[[Any], Observable[Any]],
) -> Callable[[Observable[_T1]], Observable[Tuple[_T1, _T2]]]:
    def join(source: Observable[_T1]) -> Observable[Tuple[_T1, _T2]]:
        """Correlates the elements of two sequences based on
        overlapping durations.

        Args:
            source: Source observable.

        Return:
            An observable sequence that contains elements
            combined into a tuple from source elements that have an overlapping
            duration.
        """

        left = source

        def subscribe(
            observer: abc.ObserverBase[Tuple[_T1, _T2]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            group = CompositeDisposable()
            left_done = False
            left_map: OrderedDict[int, _T1] = OrderedDict()
            left_id = 0
            right_done = False
            right_map: OrderedDict[int, _T2] = OrderedDict()
            right_id = 0

            def on_next_left(value: _T1):
                nonlocal left_id
                duration = None
                current_id = left_id
                left_id += 1
                md = SingleAssignmentDisposable()

                left_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in left_map:
                        del left_map[current_id]
                    if not len(left_map) and left_done:
                        observer.on_completed()

                    group.remove(md)

                try:
                    duration = left_duration_mapper(value)
                except Exception as exception:
                    observer.on_error(exception)
                    return

                md.disposable = duration.pipe(take(1)).subscribe(
                    noop, observer.on_error, lambda: expire(), scheduler=scheduler
                )

                for val in right_map.values():
                    result = (value, val)
                    observer.on_next(result)

            def on_completed_left() -> None:
                nonlocal left_done
                left_done = True
                if right_done or not len(left_map):
                    observer.on_completed()

            group.add(
                left.subscribe(
                    on_next_left,
                    observer.on_error,
                    on_completed_left,
                    scheduler=scheduler,
                )
            )

            def on_next_right(value: _T2):
                nonlocal right_id
                duration = None
                current_id = right_id
                right_id += 1
                md = SingleAssignmentDisposable()
                right_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in right_map:
                        del right_map[current_id]
                    if not len(right_map) and right_done:
                        observer.on_completed()

                    group.remove(md)

                try:
                    duration = right_duration_mapper(value)
                except Exception as exception:
                    observer.on_error(exception)
                    return

                md.disposable = duration.pipe(take(1)).subscribe(
                    noop, observer.on_error, lambda: expire(), scheduler=scheduler
                )

                for val in left_map.values():
                    result = (val, value)
                    observer.on_next(result)

            def on_completed_right():
                nonlocal right_done
                right_done = True
                if left_done or not len(right_map):
                    observer.on_completed()

            group.add(
                right.subscribe(
                    on_next_right,
                    observer.on_error,
                    on_completed_right,
                    scheduler=scheduler,
                )
            )
            return group

        return Observable(subscribe)

    return join


__all__ = ["join_"]
