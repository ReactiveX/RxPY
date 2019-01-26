from rx.disposable import CompositeDisposable

from .observablebase import ObservableBase
from .observable import Observable

class GroupedObservable(ObservableBase):
    def __init__(self, key, underlying_observable, merged_disposable=None):
        super(GroupedObservable, self).__init__()
        self.key = key

        def subscribe(observer, scheduler=None):
            return CompositeDisposable(merged_disposable.disposable, underlying_observable.subscribe(observer, scheduler=scheduler))

        self.underlying_observable = underlying_observable if not merged_disposable else Observable(subscribe)

    def _subscribe_core(self, observer, scheduler=None):
        return self.underlying_observable.subscribe(observer, scheduler=scheduler)
