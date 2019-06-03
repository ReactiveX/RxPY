import logging
from typing import Callable, Any
from collections import OrderedDict

from rx import operators as ops
from rx.core import Observable
from rx.internal.utils import add_ref
from rx.disposable import SingleAssignmentDisposable, RefCountDisposable, CompositeDisposable
from rx.subject import Subject

log = logging.getLogger("Rx")


def _group_join(right: Observable,
                left_duration_mapper: Callable[[Any], Observable],
                right_duration_mapper: Callable[[Any], Observable],
               ) -> Callable[[Observable], Observable]:
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

    def nothing(_):
        return None

    def group_join(left: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            group = CompositeDisposable()
            rcd = RefCountDisposable(group)
            left_map = OrderedDict()
            right_map = OrderedDict()
            left_id = [0]
            right_id = [0]

            def on_next_left(value):
                subject = Subject()

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

                def on_error(error):
                    for left_value in left_map.values():
                        left_value.on_error(error)

                    observer.on_error(error)

                md.disposable = duration.pipe(ops.take(1)).subscribe_(nothing, on_error, expire, scheduler)

            def on_error_left(error):
                for left_value in left_map.values():
                    left_value.on_error(error)

                observer.on_error(error)

            group.add(left.subscribe_(on_next_left, on_error_left, observer.on_completed, scheduler))

            def send_right(value):
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

                def on_error(error):
                    with left.lock:
                        for left_value in left_map.values():
                            left_value.on_error(error)

                        observer.on_error(error)

                md.disposable = duration.pipe(ops.take(1)).subscribe_(nothing, on_error, expire, scheduler)

                with left.lock:
                    for left_value in left_map.values():
                        left_value.on_next(value)

            def on_error_right(error):
                for left_value in left_map.values():
                    left_value.on_error(error)

                observer.on_error(error)

            group.add(right.subscribe_(send_right, on_error_right, scheduler=scheduler))
            return rcd
        return Observable(subscribe)
    return group_join
