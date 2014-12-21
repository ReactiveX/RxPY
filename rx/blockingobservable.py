from rx import Observable

class BlockingObservable(Observable):
    def __init__(self, observable=None):
        self.observable = observable
        super(BlockingObservable, self).__init__(observable.subscribe)
