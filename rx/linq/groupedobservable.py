from rx import AnonymousObservable, Observable
from rx.disposables import CompositeDisposable

class GroupedObservable(Observable):
    def __init__(self, key, underlying_observable, merged_disposable=None):
        super(GroupedObservable, self).__init__(self.subscribe)
        self.key = key

        def subscribe(observer):
            return CompositeDisposable(merged_disposable.disposable, underlying_observable.subscribe(observer))

        self.underlying_observable = underlying_observable if not merged_disposable else AnonymousObservable(subscribe)

    def subscribe(self, on_next=None, on_error=None, on_completed=None):
        return self.underlying_observable.subscribe(on_next, on_error, on_completed)
