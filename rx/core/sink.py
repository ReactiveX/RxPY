import threading
from typing import Any

from .typing import Disposable, Observer
from .anonymousobserver import NoopObserver


class Sink(Disposable):
    """Base class for implementation of query operators, providing a
    lightweight sink that can be disposed to mute the outgoing
    observer.

    Implementations of sinks are responsible to enforce the message
    grammar on the associated observer. Upon sending a terminal
    message, a pairing dispose call should be made to trigger
    cancellation of related resources and to mute the outgoing
    observer."""

    def __init__(self, observer: Observer, cancel: Disposable) -> None:
        self._observer = observer
        self._cancel = cancel
        self.lock = threading.RLock()

    def dispose(self):
        self._observer = NoopObserver()

        with self.lock:
            if self._cancel:
                self._cancel.dispose()
                self._cancel = None

    def get_forwarder(self):
        return Sink._(self)

    class _(Observer):
        def __init__(self, forward: Sink) -> None:
            self._forward = forward

        def send(self, value: Any) -> None:
            self._forward._observer.send(value)

        def throw(self, error: Exception) -> None:
            self._forward._observer.throw(error)
            self._forward.dispose()

        def close(self) -> None:
            self._forward._observer.close()
            self._forward.dispose()
