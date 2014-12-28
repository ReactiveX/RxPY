from rx import Observable
from rx.disposables import Disposable
from rx.subjects import Subject
from rx.internal.utils import check_disposed


class ControlledSubject(Observable):
    def __init__(self, enable_queue=True):
        super(ControlledSubject, self).__init__(self._subscribe)

        self.subject = Subject()
        self.enable_queue = enable_queue
        self.queue = [] if enable_queue else None
        self.requested_count = 0
        self.requested_disposable = Disposable.empty()
        self.error = None
        self.has_failed = False
        self.has_completed = False
        self.controlled_disposable = Disposable.empty()

    def _subscribe(self, observer):
        return self.subject.subscribe(observer)

    def on_completed(self):
        check_disposed(self)
        self.has_completed = True

        if not self.enable_queue or not len(self.queue):
            self.subject.on_completed()

    def on_error(self, error):
        check_disposed(self)
        self.has_failed = True
        self.error = error

        if not self.enable_queue or not len(self.queue):
            self.subject.on_error(error)

    def on_next(self, value):
        check_disposed(self)
        has_requested = False

        if not self.requested_count:
            if self.enable_queue:
                self.queue.append(value)
        else:
            if self.requested_count != -1:
                requested_count = self.requested_count
                self.requested_count -= 1
                if requested_count == 0:
                    self.dispose_current_request()

            has_requested = True

        if has_requested:
            self.subject.on_next(value)

    def _process_request(self, number_of_items):
        if self.enable_queue:
            #console.log('queue length', self.queue.length)

            while len(self.queue) >= number_of_items and number_of_items > 0:
                # console.log('number of items', number_of_items)
                self.subject.on_next(self.queue.shift())
                number_of_items -= 1

            if len(self.queue):
                return {"number_of_items": number_of_items, "return_value": True}
            else:
                return {"number_of_items": number_of_items, "return_value": False}

        if self.has_failed:
            self.subject.on_error(self.error)
            self.controlled_disposable.dispose()
            self.controlled_disposable = Disposable.empty()
        elif self.has_completed:
            self.subject.on_completed()
            self.controlled_disposable.dispose()
            self.controlled_disposable = Disposable.empty()

        return {"number_of_items": number_of_items, "return_value": False}

    def request(self, number):
        check_disposed(self)
        self.dispose_current_request()

        r = self._process_request(number)
        number = r["number_of_items"]
        if not r["return_value"]:
            self.requested_count = number

            def action():
                self.requested_count = 0
            self.requested_disposable = Disposable(action)

            return self.requested_disposable
        else:
            return Disposable.empty()

    def dispose_current_request(self):
        self.requested_disposable.dispose()
        self.requested_disposable = Disposable.empty()

    def dispose(self):
        self.is_disposed = True # FIXME: something wrong in RxJS?
        self.error = None
        self.subject.dispose()
        self.requested_disposable.dispose()
