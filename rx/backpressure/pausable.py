from six import add_metaclass

from rx import Observable
from rx.internal import ExtensionMethod
from rx.disposables import CompositeDisposable, Disposable
from rx.subjects import Subject

class PausableObservable(Observable):
    def __init__(self, source, subject=None):
        self.source = source
        self.subject = subject or Subject()
        self.is_paused = True
        super(PausableObservable, self).__init__(self, self.subscribe)

    def subscribe(self, observer):
        conn = self.source.publish()
        subscription = conn.subscribe(observer)
        connection = Disposable.empty()

        def on_next(b):
            if b:
                connection = conn.connect()
            else:
                connection.dispose()
                connection = Disposable.empty()

        pausable = self.subject.distinct_until_changed().subscribe(on_next)
        return CompositeDisposable(subscription, connection, pausable)

    def pause(self):
        if self.is_paused:
            return

        self.is_paused = True
        self.subject.on_next(False)

    def resume(self):
        if not self.is_paused:
            return

        self.is_paused = False
        self.subject.on_next(True)

@add_metaclass(ExtensionMethod)
class ObservablePausable(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def pausable(self, pauser):
        """Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False.

        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable(pauser)

        Keyword parameters:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.

        Returns the observable {Observable} sequence which is paused based upon
        the pauser."""

        return PausableObservable(self, pauser)
