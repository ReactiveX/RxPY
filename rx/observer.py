
class Observer(object):
    def __init__(self, on_next, on_completed=None, on_error=None):
        self.on_next = on_next
        self._on_completed = on_completed
        self._on_error = on_error

    def on_completed(self):
        if self._on_completed:
            self._on_completed()

    def on_error(self, ex):
        if self._on_error:
            self._on_error(ex)

