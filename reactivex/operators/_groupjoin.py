import logging
from collections import OrderedDict
from typing import Any, Callable, Optional, Tuple, TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import add_ref
from reactivex.subject import Subject

_TLeft = TypeVar("_TLeft")
_TRight = TypeVar("_TRight")

log = logging.getLogger("Rx")


def group_join_(
    right: Observable[_TRight],
    left_duration_mapper: Callable[[_TLeft], Observable[Any]],
    right_duration_mapper: Callable[[_TRight], Observable[Any]],
) -> Callable[[Observable[_TLeft]], Observable[Tuple[_TLeft, Observable[_TRight]]]]:
    """Correlates the elements of two sequences based on overlapping
    durations, and groups the results.

    Args:
        right: The right observable sequence to join elements for.
        left_duration_mapper: A function to select the duration (expressed
            as an observable sequence) of each element of the left observable
            sequence, used to determine overlap.
        right_duration_mapper: A function to select the duration (expressed
            as an observable sequence) of each element of the right observable
            sequence, used to determine overlap.

    Returns:
        An observable sequence that contains elements combined into a tuple
    from source elements that have an overlapping duration.
    """

    def nothing(_: Any) -> None:
        return None

    def group_join(
        left: Observable[_TLeft],
    ) -> Observable[Tuple[_TLeft, Observable[_TRight]]]:
        def subscribe(
            observer: abc.ObserverBase[Tuple[_TLeft, Observable[_TRight]]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            group = CompositeDisposable()
            rcd = RefCountDisposable(group)
            left_map: OrderedDict[int, Subject[_TRight]] = OrderedDict()
            right_map: OrderedDict[int, _TRight] = OrderedDict()
            left_id = [0]
            right_id = [0]

            def on_next_left(value: _TLeft) -> None:
                subject: Subject[_TRight] = Subject()

                with left.lock:
                    _id = left_id[0]
                    left_id[0] += 1
                    left_map[_id] = subject

                try:
                    result = (value, add_ref(subject, rcd))
                except Exception as e:
                    log.error("*** Exception: %s" % e)
                    for left_value in left_map.values():
                        left_value.on_error(e)

                    observer.on_error(e)
                    return

                observer.on_next(result)

                for right_value in right_map.values():
                    subject.on_next(right_value)

                md = SingleAssignmentDisposable()
                group.add(md)

                def expire():
                    if _id in left_map:
                        del left_map[_id]
                        subject.on_completed()

                    group.remove(md)

                try:
                    duration = left_duration_mapper(value)
                except Exception as e:
                    for left_value in left_map.values():
                        left_value.on_error(e)

                    observer.on_error(e)
                    return

                def on_error(error: Exception) -> Any:
                    for left_value in left_map.values():
                        left_value.on_error(error)

                    observer.on_error(error)

                md.disposable = duration.pipe(ops.take(1)).subscribe(
                    nothing, on_error, expire, scheduler=scheduler
                )

            def on_error_left(error: Exception) -> None:
                for left_value in left_map.values():
                    left_value.on_error(error)

                observer.on_error(error)

            group.add(
                left.subscribe(
                    on_next_left,
                    on_error_left,
                    observer.on_completed,
                    scheduler=scheduler,
                )
            )

            def send_right(value: _TRight) -> None:
                with left.lock:
                    _id = right_id[0]
                    right_id[0] += 1
                    right_map[_id] = value

                md = SingleAssignmentDisposable()
                group.add(md)

                def expire():
                    del right_map[_id]
                    group.remove(md)

                try:
                    duration = right_duration_mapper(value)
                except Exception as e:
                    for left_value in left_map.values():
                        left_value.on_error(e)

                    observer.on_error(e)
                    return

                def on_error(error: Exception):
                    with left.lock:
                        for left_value in left_map.values():
                            left_value.on_error(error)

                        observer.on_error(error)

                md.disposable = duration.pipe(ops.take(1)).subscribe(
                    nothing, on_error, expire, scheduler=scheduler
                )

                with left.lock:
                    for left_value in left_map.values():
                        left_value.on_next(value)

            def on_error_right(error: Exception) -> None:
                for left_value in left_map.values():
                    left_value.on_error(error)

                observer.on_error(error)

            group.add(right.subscribe(send_right, on_error_right, scheduler=scheduler))
            return rcd

        return Observable(subscribe)

    return group_join


__all__ = ["group_join_"]
