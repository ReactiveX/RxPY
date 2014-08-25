from datetime import timedelta

from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal.basic import default_key_serializer, identity
from rx.internal import ArgumentOutOfRangeException
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSkipLastWithTime(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def skip_last_with_time(self, duration, scheduler):
        """Skips elements for the specified duration from the end of the
        observable source sequence, using the specified scheduler to run timers.

        1 - res = source.skip_last_with_time(5000)
        2 - res = source.skip_last_with_time(5000, scheduler)

        Description:
        This operator accumulates a queue with a length enough to store elements
        received during the initial duration window. As more elements are
        received, elements older than the specified duration are taken from the
        queue and produced on the result sequence. This causes elements to be
        delayed with duration.

        Keyword arguments:
        duration -- {Number} Duration for skipping elements from the end of the
            sequence.
        scheduler -- {Scheduler} [Optional]  Scheduler to run the timer on. If
            not specified, defaults to Rx.Scheduler.timeout
        Returns an observable {Observable} sequence with the elements skipped
        during the specified duration from the end of the source sequence."""

        scheduler = scheduler or timeout_scheduler
        source = self

        if isinstance(duration, int):
            duration = timedelta(milliseconds=duration)

        def subscribe(observer):
            q = []

            def on_next(x):
                now = scheduler.now()
                q.append({ "interval": now, "value": x })
                print(now, q[0], duration)
                while len(q) and now - q[0]["interval"] >= duration:
                    observer.on_next(q.pop(0)["value"])

            def on_completed():
                now = scheduler.now()
                while len(q) and now - q[0]["interval"] >= duration:
                    observer.on_next(q.pop(0)["value"])

                observer.on_completed()

            return source.subscribe(on_next, observer.on_error, on_completed)
        return AnonymousObservable(subscribe)
