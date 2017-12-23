
from rx.core import ObservableBase, Disposable
from rx.disposables import CompositeDisposable
from rx.subjects import Subject


class PausableObservable(ObservableBase):
    def __init__(self, source, pauser=None):
        self.source = source
        self.controller = Subject()

        if pauser and hasattr(pauser, "subscribe"):
            self.pauser = self.controller.merge(pauser)
        else:
            self.pauser = self.controller

        super(PausableObservable, self).__init__()

    def _subscribe_core(self, observer, scheduler=None):
        conn = self.source.publish()
        subscription = conn.subscribe(observer)
        connection = [Disposable.empty()]

        def send(value):
            if value:
                connection[0] = conn.connect()
            else:
                connection[0].dispose()
                connection[0] = Disposable.empty()

        pausable = self.pauser.distinct_until_changed().subscribe_callbacks(send, scheduler=scheduler)
        return CompositeDisposable(subscription, connection[0], pausable)

    def pause(self):
        self.controller.send(False)

    def resume(self):
        self.controller.send(True)

