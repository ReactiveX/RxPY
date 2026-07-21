from typing import Any, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import curry_flip
from reactivex.scheduler import ImmediateScheduler

_T = TypeVar("_T")


@curry_flip
def expand_(
    source: Observable[_T],
    mapper: typing.Mapper[_T, Observable[_T]],
) -> Observable[_T]:
    """Expands an observable sequence by recursively invoking
    mapper.

    Examples:
        >>> source.pipe(expand(lambda x: of(x * 2)))
        >>> expand(lambda x: of(x * 2))(source)

    Args:
        source: Source observable to expand.
        mapper: Function to recursively map elements.

    Returns:
        An observable sequence containing all the elements produced
        by the recursive expansion.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        scheduler = scheduler or ImmediateScheduler.singleton()

        queue: list[Observable[_T]] = []
        m = SerialDisposable()
        d = CompositeDisposable(m)
        active_count = 0
        is_acquired = False

        def ensure_active():
            nonlocal is_acquired

            is_owner = False
            if queue:
                is_owner = not is_acquired
                is_acquired = True

            def action(scheduler: abc.SchedulerBase, state: Any = None):
                nonlocal is_acquired, active_count

                if queue:
                    work = queue.pop(0)
                else:
                    is_acquired = False
                    return

                sad = SingleAssignmentDisposable()
                d.add(sad)

                def on_next(value: _T) -> None:
                    nonlocal active_count

                    observer.on_next(value)
                    result = None
                    try:
                        result = mapper(value)
                    except Exception as ex:
                        observer.on_error(ex)
                        return

                    queue.append(result)
                    active_count += 1
                    ensure_active()

                def on_complete() -> None:
                    nonlocal active_count

                    d.remove(sad)
                    active_count -= 1
                    if active_count == 0:
                        observer.on_completed()

                sad.disposable = work.subscribe(
                    on_next, observer.on_error, on_complete, scheduler=scheduler
                )
                m.disposable = scheduler.schedule(action)

            if is_owner:
                m.disposable = scheduler.schedule(action)

        queue.append(source)
        active_count += 1
        ensure_active()
        return d

    return Observable(subscribe)


__all__ = ["expand_"]
