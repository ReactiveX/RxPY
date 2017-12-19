from rx.core import AnonymousObservable, ObservableBase
from rx.concurrency import timeout_scheduler
from rx.internal.utils import add_ref
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable, \
    RefCountDisposable, SerialDisposable
from rx.subjects import Subject


def window_with_time_or_count(source, timespan, count) -> ObservableBase:

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler

        n = [0]
        s = [None]
        timer_d = SerialDisposable()
        window_id = [0]
        group_disposable = CompositeDisposable(timer_d)
        ref_count_disposable = RefCountDisposable(group_disposable)

        def create_timer(_id):
            m = SingleAssignmentDisposable()
            timer_d.disposable = m

            def action(scheduler, state):
                if _id != window_id[0]:
                    return

                n[0] = 0
                window_id[0] += 1
                new_id = window_id[0]
                s[0].close()
                s[0] = Subject()
                observer.send(add_ref(s[0], ref_count_disposable))
                create_timer(new_id)

            m.disposable = scheduler.schedule_relative(timespan, action)

        s[0] = Subject()
        observer.send(add_ref(s[0], ref_count_disposable))
        create_timer(0)

        def send(x):
            new_window = False
            new_id = 0

            s[0].send(x)
            n[0] += 1
            if n[0] == count:
                new_window = True
                n[0] = 0
                window_id[0] += 1
                new_id = window_id[0]
                s[0].close()
                s[0] = Subject()
                observer.send(add_ref(s[0], ref_count_disposable))

            if new_window:
                create_timer(new_id)

        def throw(e):
            s[0].throw(e)
            observer.throw(e)

        def close():
            s[0].close()
            observer.close()

        group_disposable.add(source.subscribe_callbacks(send, throw, close, scheduler))
        return ref_count_disposable
    return AnonymousObservable(subscribe)

