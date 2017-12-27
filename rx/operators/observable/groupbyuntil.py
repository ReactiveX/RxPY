from collections import OrderedDict

from rx.core import ObservableBase, AnonymousObservable, GroupedObservable
from rx.subjects import Subject
from rx.disposables import CompositeDisposable, RefCountDisposable, \
    SingleAssignmentDisposable
from rx.internal.basic import identity


def group_by_until(self, key_mapper, element_mapper, duration_mapper) -> ObservableBase:
    """Groups the elements of an observable sequence according to a
    specified key mapper function. A duration mapper function is used
    to control the lifetime of groups. When a group expires, it receives
    an OnCompleted notification. When a new element with the same key value
    as a reclaimed group occurs, the group will be reborn with a new
    lifetime request.

    1 - observable.group_by_until(
            lambda x: x.id,
            None,
            lambda : Rx.Observable.never()
        )
    2 - observable.group_by_until(
            lambda x: x.id,
            lambda x: x.name,
            lambda: Rx.Observable.never()
        )
    3 - observable.group_by_until(
            lambda x: x.id,
            lambda x: x.name,
            lambda:  Rx.Observable.never(),
            lambda x: str(x))

    Keyword arguments:
    key_mapper -- A function to extract the key for each element.
    duration_mapper -- A function to signal the expiration of a group.

    Returns a sequence of observable groups, each of which corresponds to
    a unique key value, containing all elements that share that same key
    value. If a group's lifetime expires, a new group with the same key
    value can be created once an element with such a key value is
    encountered.
    """

    source = self
    element_mapper = element_mapper or identity

    def subscribe(observer, scheduler=None):
        writers = OrderedDict()
        group_disposable = CompositeDisposable()
        ref_count_disposable = RefCountDisposable(group_disposable)

        def send(x):
            writer = None
            key = None

            try:
                key = key_mapper(x)
            except Exception as e:
                for wrt in writers.values():
                    wrt.throw(e)

                observer.throw(e)
                return

            fire_new_map_entry = False
            writer = writers.get(key)
            if not writer:
                writer = Subject()
                writers[key] = writer
                fire_new_map_entry = True

            if fire_new_map_entry:
                group = GroupedObservable(key, writer, ref_count_disposable)
                duration_group = GroupedObservable(key, writer)
                try:
                    duration = duration_mapper(duration_group)
                except Exception as e:
                    for wrt in writers.values():
                        wrt.throw(e)

                    observer.throw(e)
                    return

                observer.send(group)
                sad = SingleAssignmentDisposable()
                group_disposable.add(sad)

                def expire():
                    if writers[key]:
                        del writers[key]
                        writer.close()

                    group_disposable.remove(sad)

                def send(value):
                    pass

                def throw(exn):
                    for wrt in writers.values():
                        wrt.throw(exn)
                    observer.throw(exn)

                def close():
                    expire()

                sad.disposable = duration.take(1).subscribe_callbacks(send, throw, close, scheduler)

            try:
                element = element_mapper(x)
            except Exception as error:
                for wrt in writers.values():
                    wrt.throw(error)

                observer.throw(error)
                return

            writer.send(element)

        def throw(ex):
            for wrt in writers.values():
                wrt.throw(ex)

            observer.throw(ex)

        def close():
            for wrt in writers.values():
                wrt.close()

            observer.close()

        group_disposable.add(source.subscribe_callbacks(send, throw, close, scheduler))
        return ref_count_disposable
    return AnonymousObservable(subscribe)
