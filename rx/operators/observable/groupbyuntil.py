from collections import OrderedDict

from rx.core import ObservableBase, AnonymousObservable
from rx.subjects import Subject
from rx.disposables import CompositeDisposable, RefCountDisposable, \
    SingleAssignmentDisposable
from rx.internal.basic import default_comparer, identity
from rx.operators.groupedobservable import GroupedObservable
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def group_by_until(self, key_selector, element_selector, duration_selector, comparer=None):
    """Groups the elements of an observable sequence according to a
    specified key selector function. A duration selector function is used
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
    key_selector -- A function to extract the key for each element.
    duration_selector -- A function to signal the expiration of a group.
    comparer -- [Optional] {Function} Used to compare objects. When not
        specified, the default comparer is used. Note: this argument will be
        ignored in the Python implementation of Rx. Python objects knows,
        or should know how to compare themselves.

    Returns a sequence of observable groups, each of which corresponds to
    a unique key value, containing all elements that share that same key
    value. If a group's lifetime expires, a new group with the same key
    value can be created once an element with such a key value is
    encountered.
    """

    source = self
    element_selector = element_selector or identity
    comparer = comparer or default_comparer

    def subscribe(observer, scheduler=None):
        mapping = OrderedDict()
        group_disposable = CompositeDisposable()
        ref_count_disposable = RefCountDisposable(group_disposable)

        def send(x):
            writer = None
            key = None

            try:
                key = key_selector(x)
            except Exception as e:
                for w in mapping.values():
                    w.throw(e)

                observer.throw(e)
                return

            fire_new_map_entry = False
            writer = mapping.get(key)
            if not writer:
                writer = Subject()
                mapping[key] = writer
                fire_new_map_entry = True

            if fire_new_map_entry:
                group = GroupedObservable(key, writer, ref_count_disposable)
                duration_group = GroupedObservable(key, writer)
                try:
                    duration = duration_selector(duration_group)
                except Exception as e:
                    for w in mapping.values():
                        w.throw(e)

                    observer.throw(e)
                    return

                observer.send(group)
                md = SingleAssignmentDisposable()
                group_disposable.add(md)

                def expire():
                    if mapping[key]:
                        del mapping[key]
                        writer.close()

                    group_disposable.remove(md)

                def send(value):
                    pass

                def throw(exn):
                    for wr in mapping.values():
                        wr.throw(exn)
                    observer.throw(exn)

                def close():
                    expire()

                md.disposable = duration.take(1).subscribe_callbacks(send, throw, close, scheduler)

            try:
                element = element_selector(x)
            except Exception as e:
                for w in mapping.values():
                    w.throw(e)

                observer.throw(e)
                return

            def action(scheduler, state):
                writer.send(element)

            from datetime import timedelta
            scheduler.schedule_relative(timedelta(microseconds=1), action)

        def throw(ex):
            for w in mapping.values():
                w.throw(ex)

            observer.throw(ex)

        def close():
            for w in mapping.values():
                w.close()

            observer.close()

        group_disposable.add(source.subscribe_callbacks(send, throw, close, scheduler))
        return ref_count_disposable
    return AnonymousObservable(subscribe)
