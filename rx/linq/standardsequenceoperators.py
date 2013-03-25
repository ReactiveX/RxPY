
class ObservableLinq(object):
    # Observable.select extension metho
    def select(self, selector):
        # <summary>
        # Projects each element of an observable sequence into a new form by incorporating the element's index.
        # &#10;
        # &#10;1 - source.select(function (value) { return value * value; });
        # &#10;2 - source.select(function (value, index) { return value * value + index; });
        # </summary>
        # <param name="selector">A transform function to apply to each source element; the second parameter of the function represents the index of the source element.</param>
        # <returns>An observable sequence whose elements are the result of invoking the transform function on each element of source.</returns>        

        def subscribe(observer):
            count = 0

            def on_next(value):
                nonlocal count
                result = None
                try:
                    result = selector(value, count)
                except Exception as err:
                    observer.on_error(err)
                else:
                    count += 1
                    observer.on_next(result)

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return self.__class__(subscribe)

    def take(self, count, scheduler=None):
        if count < 0:
            raise Exception(argumentOutOfRange)
        
        if not count:
            return Observable.empty(scheduler)
        
        def subscribe(observer):
            nonlocal count
            remaining = count

            def on_next(x):
                if remaining > 0:
                    remaining -= 1
                    observer.on_next(x)
                    if not remaining:
                        observer.on_completed()

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return self.__class__(subscribe)
