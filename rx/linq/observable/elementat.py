from rx import Observable, AnonymousObservable
from rx.internal import extends

from .elementatordefault import ElementAtOrDefault

@extends(Observable)
class ElementAt(object):


    def element_at(self, index):
        """Returns the element at a specified index in a sequence.

        Example:
        res = source.element_at(5)

        Keyword arguments:
        index -- {Number} The zero-based index of the element to retrieve.

        Returns an observable {Observable} sequence that produces the element at
        the specified position in the source sequence."""

        return ElementAtOrDefault._element_at_or_default(self, index,
                                                                   False)
