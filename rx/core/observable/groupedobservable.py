from rx.disposables import CompositeDisposable

from .observable import Observable
from .anonymousobservable import AnonymousObservable

class GroupedObservable(Observable):
    def __init__(self, key, underlying_observable, merged_disposable=None):
        super(GroupedObservable, self).__init__()
        self.key = key

        def subscribe(observer, scheduler=None):
            return CompositeDisposable(merged_disposable.disposable, underlying_observable.subscribe(observer, scheduler))

        self.underlying_observable = underlying_observable if not merged_disposable else AnonymousObservable(subscribe)

    def _subscribe_core(self, observer, scheduler=None):
        return self.underlying_observable.subscribe(observer, scheduler)
