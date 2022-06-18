from collections import OrderedDict
from typing import Any, Callable, Optional, TypeVar, cast

from reactivex import GroupedObservable, Observable, abc
from reactivex import operators as ops
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal.basic import identity
from reactivex.subject import Subject
from reactivex.typing import Mapper

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


def group_by_until_(
    key_mapper: Mapper[_T, _TKey],
    element_mapper: Optional[Mapper[_T, _TValue]],
    duration_mapper: Callable[[GroupedObservable[_TKey, _TValue]], Observable[Any]],
    subject_mapper: Optional[Callable[[], Subject[_TValue]]] = None,
) -> Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function. A duration mapper function is used
    to control the lifetime of groups. When a group expires, it receives
    an OnCompleted notification. When a new element with the same key
    value as a reclaimed group occurs, the group will be reborn with a
    new lifetime request.

    Examples:
        >>> group_by_until(lambda x: x.id, None, lambda : reactivex.never())
        >>> group_by_until(
            lambda x: x.id,lambda x: x.name, lambda grp: reactivex.never()
        )
        >>> group_by_until(
            lambda x: x.id,
            lambda x: x.name,
            lambda grp: reactivex.never(),
            lambda: ReplaySubject()
        )

    Args:
        key_mapper: A function to extract the key for each element.
        duration_mapper: A function to signal the expiration of a group.
        subject_mapper: A function that returns a subject used to initiate
            a grouped observable. Default mapper returns a Subject object.

    Returns: a sequence of observable groups, each of which corresponds to
    a unique key value, containing all elements that share that same key
    value. If a group's lifetime expires, a new group with the same key
    value can be created once an element with such a key value is
    encountered.
    """

    element_mapper_ = element_mapper or cast(Mapper[_T, _TValue], identity)

    default_subject_mapper: Callable[[], Subject[_TValue]] = lambda: Subject()
    subject_mapper_ = subject_mapper or default_subject_mapper

    def group_by_until(
        source: Observable[_T],
    ) -> Observable[GroupedObservable[_TKey, _TValue]]:
        def subscribe(
            observer: abc.ObserverBase[GroupedObservable[_TKey, _TValue]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            writers: OrderedDict[_TKey, Subject[_TValue]] = OrderedDict()
            group_disposable = CompositeDisposable()
            ref_count_disposable = RefCountDisposable(group_disposable)

            def on_next(x: _T) -> None:
                writer = None
                key = None

                try:
                    key = key_mapper(x)
                except Exception as e:
                    for wrt in writers.values():
                        wrt.on_error(e)

                    observer.on_error(e)
                    return

                fire_new_map_entry = False
                writer = writers.get(key)
                if not writer:
                    try:
                        writer = subject_mapper_()
                    except Exception as e:
                        for wrt in writers.values():
                            wrt.on_error(e)

                        observer.on_error(e)
                        return

                    writers[key] = writer
                    fire_new_map_entry = True

                if fire_new_map_entry:
                    group: GroupedObservable[_TKey, _TValue] = GroupedObservable(
                        key, writer, ref_count_disposable
                    )
                    duration_group: GroupedObservable[_TKey, Any] = GroupedObservable(
                        key, writer
                    )
                    try:
                        duration = duration_mapper(duration_group)
                    except Exception as e:
                        for wrt in writers.values():
                            wrt.on_error(e)

                        observer.on_error(e)
                        return

                    observer.on_next(group)
                    sad = SingleAssignmentDisposable()
                    group_disposable.add(sad)

                    def expire() -> None:
                        if writers[key]:
                            del writers[key]
                            writer.on_completed()

                        group_disposable.remove(sad)

                    def on_next(value: Any) -> None:
                        pass

                    def on_error(exn: Exception) -> None:
                        for wrt in writers.values():
                            wrt.on_error(exn)
                        observer.on_error(exn)

                    def on_completed() -> None:
                        expire()

                    sad.disposable = duration.pipe(
                        ops.take(1),
                    ).subscribe(on_next, on_error, on_completed, scheduler=scheduler)

                try:
                    element = element_mapper_(x)
                except Exception as error:
                    for wrt in writers.values():
                        wrt.on_error(error)

                    observer.on_error(error)
                    return

                writer.on_next(element)

            def on_error(ex: Exception) -> None:
                for wrt in writers.values():
                    wrt.on_error(ex)

                observer.on_error(ex)

            def on_completed() -> None:
                for wrt in writers.values():
                    wrt.on_completed()

                observer.on_completed()

            group_disposable.add(
                source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)
            )
            return ref_count_disposable

        return Observable(subscribe)

    return group_by_until


__all__ = ["group_by_until_"]
