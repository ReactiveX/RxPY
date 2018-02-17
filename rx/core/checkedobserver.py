from rx.internal.exceptions import ReEntracyException, CompletedException

from . import Observer


class CheckedObserver(Observer):

    def __init__(self, observer):
        self._observer = observer
        self._state = 0  # 0 - idle, 1 - busy, 2 - done

    def on_next(self, value):
        self.check_access()
        try:
            self._observer.on_next(value)
        finally:
            self._state = 0

    def on_error(self, error):
        self.check_access()
        try:
            self._observer.on_error(error)
        finally:
            self._state = 2

    def on_completed(self):
        self.check_access()
        try:
            self._observer.on_completed()
        finally:
            self._state = 2

    def check_access(self):
        """Checks access to the observer for grammar violations.

        OnNext* (OnError | OnCompleted)?
        """

        if self._state == 1:
            raise ReEntracyException()
        if self._state == 2:
            raise CompletedException()
        if self._state == 0:
            self._state = 1



