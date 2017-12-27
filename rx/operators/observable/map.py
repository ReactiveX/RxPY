from rx.core import Disposable
from rx.core import Observer, ObservableBase, AnonymousObservable
from rx.core.typing import Mapper, MapperIndexed, Scheduler

# pylint: disable=W0622
def map(source: ObservableBase,
        mapper: Mapper = None,
        mapper_indexed: MapperIndexed = None
       ) -> ObservableBase:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    1 - source.map(lambda value, index: value * value + index)

    Keyword arguments:
    mapper -- A transform function to apply to each source element; the
        second parameter of the function represents the index of the
        source element
    mapper_indexed -- A transform function to apply to each source
        element; the second parameter of the function represents the
        index of the source element.

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of the source.
    """

    def subscribe(observer: Observer, scheduler: Scheduler) -> Disposable:
        count = 0

        def send(value):
            nonlocal count

            try:
                result = mapper(value) if mapper else mapper_indexed(value, count)
            except Exception as err:  # By design. pylint: disable=W0703
                observer.throw(err)
            else:
                count += 1
                observer.send(result)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
