from typing import Any
from rx.core import Disposable
from rx.core.typing import Mapper, MapperIndexed, Scheduler, Observable, Observer
from rx.streams import SingleStream


class Map(Observable):
    """Map operator implementation."""

    def __init__(self, mapper: Mapper = None, mapper_indexed: MapperIndexed = None) -> None:
        self.source = None  # type: Observable
        self.mapper = mapper
        self.mapper_indexed = mapper_indexed

        assert not (self.mapper and self.mapper_indexed)

    def subscribe(self, observer: Observer = None, scheduler: Scheduler = None) -> Disposable:
        stream = Map._(self.mapper, self.mapper_indexed).chain(observer, scheduler)
        stream.subscription = self.source.subscribe(stream, scheduler)

        return Disposable.create(stream.dispose)

    def __call__(self, source: Observable) -> Observable:
        self.source = source
        return self

    class _(SingleStream):
        def __init__(self, mapper: Mapper, mapper_indexed: MapperIndexed) -> None:
            super().__init__()

            self.count = 0
            self.mapper = mapper
            self.mapper_indexed = mapper_indexed

        def send(self, value: Any) -> None:
            try:
                if self.mapper:
                    result = self.mapper(value)
                else:
                    result = self.mapper_indexed(value, self.count)
            except Exception as err:  # By design. pylint: disable=W0703
                self.throw(err)
            else:
                self.count += 1
                self._observer.send(result)


def map(mapper: Mapper = None, mapper_indexed: MapperIndexed = None) -> Map: # pylint: disable=W0622
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
    return Map(mapper, mapper_indexed)
