from typing import Callable, Optional
from collections import OrderedDict

from rx import operators as ops
from rx.core import Observable, GroupedObservable
from rx.core.typing import Mapper
from rx.subject import Subject
from rx.disposable import CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable
from rx.internal.basic import identity


def _group_by_until(key_mapper: Mapper,
                    element_mapper: Optional[Mapper],
                    duration_mapper: Callable[[GroupedObservable], Observable],
                    subject_mapper: Optional[Callable[[], Subject]] = None,
                    ) -> Callable[[Observable], Observable]:
    """Groups the elements of an observable sequence according to a
    specified key mapper function. A duration mapper function is used
    to control the lifetime of groups. When a group expires, it receives
    an OnCompleted notification. When a new element with the same key
    value as a reclaimed group occurs, the group will be reborn with a
    new lifetime request.

    Examples:
        >>> group_by_until(lambda x: x.id, None, lambda : rx.never())
        >>> group_by_until(lambda x: x.id,lambda x: x.name, lambda grp: rx.never())
        >>> group_by_until(lambda x: x.id, lambda x: x.name, lambda grp: rx.never(), lambda: ReplaySubject())

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

    element_mapper = element_mapper or identity

    default_subject_mapper = Subject
    subject_mapper = subject_mapper or default_subject_mapper

    def group_by_until(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            writers = OrderedDict()
            group_disposable = CompositeDisposable()
            ref_count_disposable = RefCountDisposable(group_disposable)

            def on_next(x):
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
                        writer = subject_mapper()
                    except Exception as e:
                        for wrt in writers.values():
                            wrt.on_error(e)

                        observer.on_error(e)
                        return

                    writers[key] = writer
                    fire_new_map_entry = True

                if fire_new_map_entry:
                    group = GroupedObservable(key, writer, ref_count_disposable)
                    duration_group = GroupedObservable(key, writer)
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

                    def expire():
                        if writers[key]:
                            del writers[key]
                            writer.on_completed()

                        group_disposable.remove(sad)

                    def on_next(value):
                        pass

                    def on_error(exn):
                        for wrt in writers.values():
                            wrt.on_error(exn)
                        observer.on_error(exn)

                    def on_completed():
                        expire()

                    sad.disposable = duration.pipe(ops.take(1)).subscribe_(on_next, on_error, on_completed, scheduler)

                try:
                    element = element_mapper(x)
                except Exception as error:
                    for wrt in writers.values():
                        wrt.on_error(error)

                    observer.on_error(error)
                    return

                writer.on_next(element)

            def on_error(ex):
                for wrt in writers.values():
                    wrt.on_error(ex)

                observer.on_error(ex)

            def on_completed():
                for wrt in writers.values():
                    wrt.on_completed()

                observer.on_completed()

            group_disposable.add(source.subscribe_(on_next, on_error, on_completed, scheduler))
            return ref_count_disposable
        return Observable(subscribe)
    return group_by_until
