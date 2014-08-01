from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal import ExtensionMethod
from rx.subjects import Subject
from rx.disposables import CompositeDisposable

def combine_latest_source(source, subject, result_selector):
    def subscribe(observer):
        has_value = [False, False]
        has_value_all = [False]
        is_done = [False]
        values = dict()
        
        def next(x, i):
            values[i] = x
            has_value[i] = True

            has_value_all[0] = has_value_all[0] or all(has_value)
            if has_value_all[0]:
                try:
                    res = result_selector(None, values)
                except Exception as ex:
                    observer.on_error(ex)
                    return

                observer.on_next(res)
            elif is_done[0]:
                observer.on_completed()

        def on_next(x):
            next(x, 0)

        def on_completed():
            is_done[0] = True
            observer.on_completed()

        return CompositeDisposable(
            source.subscribe(on_next,observer.on_error, on_completed),
            subject.subscribe(lambda x: next(x, 1), observer.on_error)
        )
    return AnonymousObservable(subscribe)

class PausableBufferedObservable(Observable):

    def __init__(self, source, subject=None):
        self.source = source
        self.subject = subject or Subject()
        self.is_paused = True
        super(PausableBufferedObservable, self).__init__(self.subscribe)

    def subscribe(self, observer):
        previous = [True]
        queue = []

        def result_selector(data, should_fire):
            return {"data": data, "should_fire": should_fire}

        def on_next(results):
            if results.should_fire and previous[0]:
                observer.on_next(results.data)

            if results.should_fire and not previous[0]:
                while len(queue):
                    observer.on_next(queue.pop(0))

                previous[0] = True
            elif not results.should_fire and not previous[0]:
                queue.append(results.data)
            elif not results.should_fire and previous[0]:
                previous[0] = False

        def on_error(err):
            # Empty buffer before sending error
            while len(queue):
                observer.on_next(queue.pop())
            observer.on_error(err)

        def on_completed():
            # Empty buffer before sending completion
            while len(queue):
                observer.on_next(queue.pop())
            observer.on_completed()

        subscription = combine_latest_source(
                self.source,
                self.subject.distinct_until_changed(),
                result_selector
            ).subscribe(on_next, on_error, on_completed)

        self.subject.on_next(False)
        return subscription

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

    def pausable_buffered(self, subject):
        """Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False, and yields the values that were
        buffered while paused.

        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable_buffered(pauser)

        Keyword arguments:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.

        Returns the observable {Observable} sequence which is paused based upon
        the pauser."""

        return PausableBufferedObservable(self, subject)
