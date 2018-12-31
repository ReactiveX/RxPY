from rx.core import ObservableBase, AnonymousObservable
from rx.core.typing import Mapper
from rx.disposables import SerialDisposable, CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import immediate_scheduler


def expand(source: ObservableBase, mapper: Mapper) -> ObservableBase:
    """Expands an observable sequence by recursively invoking mapper.

    mapper -- Selector function to invoke for each produced
        element, resulting in another sequence to which the mapper
        will be invoked recursively again.

    Returns an observable sequence containing all the elements produced
    by the recursive expansion.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or immediate_scheduler

        queue = []
        m = SerialDisposable()
        d = CompositeDisposable(m)
        active_count = [0]
        is_acquired = [False]

        def ensure_active():
            is_owner = False
            if queue:
                is_owner = not is_acquired[0]
                is_acquired[0] = True

            def action(scheduler, state):
                if queue:
                    work = queue.pop(0)
                else:
                    is_acquired[0] = False
                    return

                sad = SingleAssignmentDisposable()
                d.add(sad)

                def on_next(value):
                    observer.on_next(value)
                    result = None
                    try:
                        result = mapper(value)
                    except Exception as ex:
                        observer.on_error(ex)
                        return

                    queue.append(result)
                    active_count[0] += 1
                    ensure_active()

                def on_complete():
                    d.remove(sad)
                    active_count[0] -= 1
                    if active_count[0] == 0:
                        observer.on_completed()

                sad.disposable = work.subscribe_(on_next, observer.on_error, on_complete, scheduler)
                m.disposable = scheduler.schedule(action)

            if is_owner:
                m.disposable = scheduler.schedule(action)

        queue.append(source)
        active_count[0] += 1
        ensure_active()
        return d
    return AnonymousObservable(subscribe)
