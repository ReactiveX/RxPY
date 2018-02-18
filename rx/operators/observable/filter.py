from typing import Any

from rx.core import Disposable
from rx.core.typing import  Predicate, PredicateIndexed, Scheduler, Observable, Observer
from rx.streams import SingleStream


class Filter(Observable):
    """Filter operator implementation."""

    def __init__(self, predicate: Predicate = None,
                 predicate_indexed: PredicateIndexed = None) -> None:
        self.source = None  # type: Observable
        self.predicate = predicate
        self.predicate_indexed = predicate_indexed

        assert not (self.predicate and self.predicate_indexed)

    def subscribe(self, observer: Observer = None, scheduler: Scheduler = None) -> Disposable:
        stream = Filter._(self.predicate, self.predicate_indexed).chain(observer, scheduler)
        stream.subscription = self.source.subscribe(stream, scheduler)

        return Disposable.create(stream.dispose)

    def __call__(self, source: Observable) -> Observable:
        self.source = source
        return self

    class _(SingleStream):
        def __init__(self, predicate: Predicate, predicate_indexed: PredicateIndexed) -> None:
            super().__init__()

            self.count = 0
            self.predicate = predicate
            self.predicate_indexed = predicate_indexed

        def on_next(self, value: Any) -> None:
            try:
                if self.predicate:
                    should_run = self.predicate(value)
                else:
                    should_run = self.predicate_indexed(value, self.count)
            except Exception as ex:  # By design. pylint: disable=W0703
                self.on_error(ex)
            else:
                self.count += 1
                if should_run:
                    self._observer.on_next(value)

# pylint: disable=W0622
def filter(predicate: Predicate = None, predicate_indexed: PredicateIndexed = None):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value: value < 10)

    Keyword arguments:
    source -- Observable sequence to filter.
    predicate --  A function to test each source element for a
        condition.
    predicate_indexed -- A function to test each source element for a
        condition; the second parameter of the function represents the
        index of the source element.

    Returns an observable sequence that contains elements from the input
    sequence that satisfy the condition.
    """

    return Filter(predicate, predicate_indexed)
