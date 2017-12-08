import logging
from collections import OrderedDict

from rx import AnonymousObservable, Observable
from rx.internal.utils import add_ref
from rx.disposables import SingleAssignmentDisposable, RefCountDisposable, \
    CompositeDisposable
from rx.subjects import Subject
from rx.internal import extensionmethod

log = logging.getLogger("Rx")


@extensionmethod(Observable)
def group_join(self, right, left_duration_selector, right_duration_selector, result_selector):
    """Correlates the elements of two sequences based on overlapping
    durations, and groups the results.

    Keyword arguments:
    right -- The right observable sequence to join elements for.
    left_duration_selector -- A function to select the duration (expressed
        as an observable sequence) of each element of the left observable
        sequence, used to determine overlap.
    right_duration_selector -- A function to select the duration (expressed
        as an observable sequence) of each element of the right observable
        sequence, used to determine overlap.
    result_selector -- A function invoked to compute a result element for
        any element of the left sequence with overlapping elements from the
        right observable sequence. The first parameter passed to the
        function is an element of the left sequence. The second parameter
        passed to the function is an observable sequence with elements from
        the right sequence that overlap with the left sequence's element.

    Returns an observable sequence that contains result elements computed
    from source elements that have an overlapping duration.
    """

    left = self

    def subscribe(observer, scheduler=None):
        nothing = lambda _: None
        group = CompositeDisposable()
        r = RefCountDisposable(group)
        left_map = OrderedDict()
        right_map = OrderedDict()
        left_id = [0]
        right_id = [0]

        def send_left(value):
            s = Subject()

            with self.lock:
                _id = left_id[0]
                left_id[0] += 1
                left_map[_id] = s

            try:
                result = result_selector(value, add_ref(s, r))
            except Exception as e:
                log.error("*** Exception: %s" % e)
                for left_value in left_map.values():
                    left_value.throw(e)

                observer.throw(e)
                return

            observer.send(result)

            for right_value in right_map.values():
                s.send(right_value)

            md = SingleAssignmentDisposable()
            group.add(md)

            def expire():
                if _id in left_map:
                    del left_map[_id]
                    s.close()

                group.remove(md)

            try:
                duration = left_duration_selector(value)
            except Exception as e:
                for left_value in left_map.values():
                    left_value.throw(e)

                observer.throw(e)
                return

            def throw(error):
                for left_value in left_map.values():
                    left_value.throw(error)

                observer.throw(error)

            md.disposable = duration.take(1).subscribe_callbacks(nothing, throw, expire, scheduler)

        def throw_left(error):
            for left_value in left_map.values():
                left_value.throw(error)

            observer.throw(error)

        group.add(left.subscribe_callbacks(send_left, throw_left, observer.close, scheduler))

        def send_right(value):
            with self.lock:
                _id = right_id[0]
                right_id[0] += 1
                right_map[_id] = value

            md = SingleAssignmentDisposable()
            group.add(md)

            def expire():
                del right_map[_id]
                group.remove(md)

            try:
                duration = right_duration_selector(value)
            except Exception as e:
                for left_value in left_map.values():
                    left_value.throw(e)

                observer.throw(e)
                return

            def throw(error):
                with self.lock:
                    for left_value in left_map.values():
                        left_value.throw(error)

                    observer.throw(error)

            md.disposable = duration.take(1).subscribe_callbacks(nothing, throw, expire, scheduler)

            with self.lock:
                for left_value in left_map.values():
                    left_value.send(value)

        def throw_right(error):
            for left_value in left_map.values():
                left_value.throw(error)

            observer.throw(error)

        group.add(right.subscribe_callbacks(send_right, throw_right, scheduler=scheduler))
        return r
    return AnonymousObservable(subscribe)
