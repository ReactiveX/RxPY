from rx.observable import Observable

# Observable.select extension method
def select(self, selector):
    # <summary>
    # Projects each element of an observable sequence into a new form by incorporating the element's index.
    # &#10;
    # &#10;1 - source.select(function (value) { return value * value; });
    # &#10;2 - source.select(function (value, index) { return value * value + index; });
    # </summary>
    # <param name="selector">A transform function to apply to each source element; the second parameter of the function represents the index of the source element.</param>
    # <returns>An observable sequence whose elements are the result of invoking the transform function on each element of source.</returns>        
    parent = self


    print (self, selector)
    def subscribe(observer):
        count = 0

        def on_next(value):
            nonlocal count
            result = None
            try:
                result = selector(value, count)
            except Exception as err:
                print (observer, err)
                observer.on_error(err)
            else:
                count += 1
                observer.on_next(result)

        return parent.subscribe(on_next, observer.on_error, observer.on_completed)
    
    return Observable(subscribe)

Observable.select = select