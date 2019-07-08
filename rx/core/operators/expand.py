from typing import Callable

from rx.core import Observable
from rx.core.typing import Mapper
from rx.disposable import SerialDisposable, CompositeDisposable, SingleAssignmentDisposable
from rx.scheduler import ImmediateScheduler


def _expand(mapper: Mapper) -> Callable[[Observable], Observable]:
    def expand(source: Observable) -> Observable:
        """Expands an observable sequence by recursively invoking
        mapper.

        Args:
            source: Source obserable to expand.

        Returns:
            An observable sequence containing all the elements produced
            by the recursive expansion.
        """
        def subscribe(observer, scheduler=None):
            scheduler = scheduler or ImmediateScheduler.singleton()

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
        return Observable(subscribe)
    return expand
