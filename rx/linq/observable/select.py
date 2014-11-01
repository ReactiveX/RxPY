from rx import Observable, AnonymousObservable

class ObservableSelect:
    """Uses a meta class to extend Observable with the methods in this class"""

    def select(self, selector):
        """Projects each element of an observable sequence into a new form by
        incorporating the element's index.

        1 - source.select(lambda value: value * value)
        2 - source.select(lambda value, index: value * value + index)

        Keyword arguments:
        selector -- A transform function to apply to each source element; the
            second parameter of the function represents the index of the source
            element.

        Returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source."""

        def subscribe(observer):
            count = [0]

            def on_next(value):
                result = None
                try:
                    result = selector(value)
                except TypeError:
                    result = selector(value, count[0])
                except Exception as err:
                    observer.on_error(err)
                else:
                    count[0] += 1
                    observer.on_next(result)

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

    map = select

Observable.select = ObservableSelect.select
Observable.map = ObservableSelect.map