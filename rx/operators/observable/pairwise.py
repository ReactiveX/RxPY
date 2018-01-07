from rx.core import ObservableBase, AnonymousObservable


def pairwise(self) -> ObservableBase:
    """Returns a new observable that triggers on the second and subsequent
    triggerings of the input observable. The Nth triggering of the input
    observable passes the arguments from the N-1th and Nth triggering as a
    pair. The argument passed to the N-1th triggering is held in hidden
    internal state until the Nth triggering occurs.

    Returns an observable {Observable} that triggers on successive pairs of
    observations from the input observable as an array.
    """

    source = self

    def subscribe(observer, scheduler=None):
        has_previous = [False]
        previous = [None]

        def send(x):
            pair = None

            with self.lock:
                if has_previous[0]:
                    pair = (previous[0], x)
                else:
                    has_previous[0] = True

                previous[0] = x

            if pair:
                observer.send(pair)

        return source.subscribe_(send, observer.throw, observer.close)
    return AnonymousObservable(subscribe)
