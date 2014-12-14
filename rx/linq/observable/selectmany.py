from rx import Observable
from rx.internal.utils import adapt_call
from rx.internal import extends

def _flat_map(source, selector):
    def projection(x, i):
        result = selector(x, i)
        return Observable.from_future(result)

    return source.map(projection).merge_observable()


@extends(Observable)
class SelectMany(object):

    def select_many(self, selector, result_selector=None):
        """One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.

        1 - source.select_many(lambda x: Observable.range(0, x))

        Or:
        Projects each element of an observable sequence to an observable
        sequence, invokes the result selector for the source element and each
        of the corresponding inner sequence's elements, and merges the results
        into one observable sequence.

        1 - source.select_many(lambda x: Observable.range(0, x), lambda x, y: x + y)

        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.

        1 - source.select_many(Observable.from_([1,2,3]))

        Keyword arguments:
        selector -- A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.
        result_selector -- [Optional] A transform function to apply to each
            element of the intermediate sequence.

        Returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence
        elements and their corresponding source element to a result element.
        """

        if result_selector:
            def projection(x, i):
                selector_result = selector(x, i)
                result = Observable.from_future(selector_result)

                return result.map(lambda y: result_selector(x, y, i))

            return this.flat_map(projection)

        if callable(selector):
            selector = adapt_call(selector)
            ret = _flat_map(self, selector)
        else:
            ret = _flat_map(self, lambda _,__: selector)

        return ret

    flat_map = select_many