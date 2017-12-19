from datetime import timedelta

from rx.core import AnonymousObservable, ObservableBase
from rx.concurrency import timeout_scheduler
from rx.internal.utils import add_ref
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable, \
    RefCountDisposable, SerialDisposable
from rx.subjects import Subject


def window_with_time(self, timespan, timeshift=None) -> ObservableBase:
    source = self

    if timeshift is None:
        timeshift = timespan

    if not isinstance(timespan, timedelta):
        timespan = timedelta(milliseconds=timespan)
    if not isinstance(timeshift, timedelta):
        timeshift = timedelta(milliseconds=timeshift)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler

        timer_d = SerialDisposable()
        next_shift = [timeshift]
        next_span = [timespan]
        total_time = [timedelta(0)]
        q = []

        group_disposable = CompositeDisposable(timer_d)
        ref_count_disposable = RefCountDisposable(group_disposable)

        def create_timer():
            m = SingleAssignmentDisposable()
            timer_d.disposable = m
            is_span = False
            is_shift = False

            if next_span[0] == next_shift[0]:
                is_span = True
                is_shift = True
            elif next_span[0] < next_shift[0]:
                is_span = True
            else:
                is_shift = True

            new_total_time = next_span[0] if is_span else next_shift[0]

            ts = new_total_time - total_time[0]
            total_time[0] = new_total_time
            if is_span:
                next_span[0] += timeshift

            if is_shift:
                next_shift[0] += timeshift

            def action(scheduler, state=None):
                s = None

                if is_shift:
                    s = Subject()
                    q.append(s)
                    observer.send(add_ref(s, ref_count_disposable))

                if is_span:
                    s = q.pop(0)
                    s.close()

                create_timer()
            m.disposable = scheduler.schedule_relative(ts, action)

        q.append(Subject())
        observer.send(add_ref(q[0], ref_count_disposable))
        create_timer()

        def send(x):
            for s in q:
                s.send(x)

        def throw(e):
            for s in q:
                s.throw(e)

            observer.throw(e)

        def close():
            for s in q:
                s.close()

            observer.close()

        group_disposable.add(source.subscribe_callbacks(send, throw, close, scheduler))
        return ref_count_disposable
    return AnonymousObservable(subscribe)
