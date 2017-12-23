from typing import Callable, Any

from rx.core import Disposable, abc
from rx.core import Observer, Observable, ObservableBase, AnonymousObservable
from rx.core import typing


def map(mapper: Callable[[Any], Any], source: ObservableBase) -> ObservableBase:
    """Project each element of an observable sequence into a new form.

    1 - source.map(lambda value: value * value)

    Keyword arguments:
    mapper -- A transform function to apply to each source element; the
        second parameter of the function represents the index of the
        source element.

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of the source.
    """

    def subscribe(observer: Observer, scheduler: typing.Scheduler) -> Disposable:
        def send(value):
            try:
                result = mapper(value)
            except Exception as err:  # By design. pylint: disable=W0703
                observer.throw(err)
            else:
                observer.send(result)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)


def map_indexed(selector: Callable[[Any, int], Any], source: ObservableBase) -> ObservableBase:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    1 - source.map(lambda value, index: value * value + index)

    Keyword arguments:
    selector -- A transform function to apply to each source element;
        the second parameter of the function represents the index of the
        source element.

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of the source.
    """

    def subscribe(observer: Observer, scheduler: abc.Scheduler) -> Disposable:
        count = 0

        def send(value):
            nonlocal count

            try:
                result = selector(value, count)
            except Exception as err:  # By design. pylint: disable=W0703
                observer.throw(err)
            else:
                count += 1
                observer.send(result)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
