import logging
from collections import OrderedDict

from rx.core import AnonymousObservable, ObservableBase
from rx.internal import noop
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable

log = logging.getLogger("Rx")


def join(source, right, left_duration_selector, right_duration_selector, result_selector) -> ObservableBase:
    """Correlates the elements of two sequences based on overlapping
    durations.

    Keyword arguments:
    right -- The right observable sequence to join elements for.
    left_duration_selector -- A function to select the duration (expressed
        as an observable sequence) of each element of the left observable
        sequence, used to determine overlap.
    right_duration_selector -- A function to select the duration (expressed
        as an observable sequence) of each element of the right observable
        sequence, used to determine overlap.
    result_selector -- A function invoked to compute a result element for
        any two overlapping elements of the left and right observable
        sequences. The parameters passed to the function correspond with
        the elements from the left and right source sequences for which
        overlap occurs.

    Return an observable sequence that contains result elements computed
    from source elements that have an overlapping duration.
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

        def send_left(value):
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
                    observer.close()

                return group.remove(md)

            try:
                duration = left_duration_selector(value)
            except Exception as exception:
                log.error("*** Exception: %s" % exception)
                observer.throw(exception)
                return

            md.disposable = duration.take(1).subscribe_callbacks(noop, observer.throw, lambda: expire(), scheduler)

            for val in right_map.values():
                try:
                    result = result_selector(value, val)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.throw(exception)
                    return

                observer.send(result)

        def close_left():
            left_done[0] = True
            if right_done[0] or not len(left_map):
                observer.close()

        group.add(left.subscribe_callbacks(send_left, observer.throw, close_left, scheduler))

        def send_right(value):
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
                    observer.close()

                return group.remove(md)

            try:
                duration = right_duration_selector(value)
            except Exception as exception:
                log.error("*** Exception: %s" % exception)
                observer.throw(exception)
                return

            md.disposable = duration.take(1).subscribe_callbacks(noop, observer.throw, lambda: expire(), scheduler)

            for val in left_map.values():
                try:
                    result = result_selector(val, value)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.throw(exception)
                    return

                observer.send(result)

        def close_right():
            right_done[0] = True
            if left_done[0] or not len(right_map):
                observer.close()

        group.add(right.subscribe_callbacks(send_right, observer.throw, close_right))
        return group
    return AnonymousObservable(subscribe)
