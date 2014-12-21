import re

from rx import AnonymousObservable, Observable
from rx.concurrency import timeout_scheduler
from rx.internal import extensionmethod, extensionclassmethod

from .coldobservable import ColdObservable
from .reactivetest import ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error

_pattern = "([a-zA-Z_0-9]|-|\([a-zA-Z1-9]*\)|[xX]|\|)"
_tokens = re.compile(_pattern)

@extensionclassmethod(Observable)
def from_string(cls, string, scheduler=None):
    """Converts a marble diagram string to an observable sequence, using an
    optional scheduler to enumerate the events.

    Special characters:
    - = Timespan of 100 ms
    x = on_error()
    | = on_completed()

    All other characters are treated as an on_next() event at the given
    moment they are found on the string.

    Examples:
    1 - res = rx.Observable.from_string("1-2-3-|")
    2 - res = rx.Observable.from_string("1-2-3-x", rx.Scheduler.timeout)

    Keyword arguments:
    string -- String with marble diagram
    scheduler -- [Optional] Scheduler to run the the input sequence on.

    Returns the observable sequence whose elements are pulled from the
    given marble diagram string.
    """

    scheduler = scheduler or timeout_scheduler

    completed = [False]
    messages = []
    timespan = [0]

    def handle_timespan(value):
        timespan[0] += 100

    def handle_on_next(value):
        messages.append(on_next(timespan[0], value))

    def handle_on_completed(value):
        messages.append(on_completed(timespan[0]))
        completed[0] = True

    def handle_on_error(value):
        messages.append(on_error(timespan[0], value))
        completed[0] = True

    specials = {
        '-' : handle_timespan,
        'x' : handle_on_error,
        'X' : handle_on_error,
        '|' : handle_on_completed
    }

    for token in cls._tokens.findall(string):
        func = specials.get(token, handle_on_next)
        func(token)

    if not completed[0]:
        messages.append(on_completed(timespan[0]))

    return ColdObservable(scheduler, messages)

@extensionmethod(Observable)
def to_string(self, scheduler=None):
    """Converts an observable sequence into a marble diagram string

    Keyword arguments:
    scheduler -- [Optional] The scheduler that was used to run the the input
        sequence on.

    Returns marble string"""

    scheduler = scheduler or timeout_scheduler
    source = self

    def subscribe(observer):
        result = []
        previously = [scheduler.now()]

        def add_timespan():
            now = scheduler.now()
            diff =  now - previously[0]
            previously[0] = now
            msecs = scheduler.to_relative(diff)
            dashes = "-" * int((msecs+50)/100)
            result.append(dashes)

        def on_next(value):
            add_timespan()
            result.append(value)

        def on_error(exception):
            add_timespan()
            result.append(exception)
            observer.on_next("".join(str(n) for n in result))
            observer.on_completed()

        def on_completed():
            add_timespan()
            result.append("|")
            observer.on_next("".join(str(n) for n in result))
            observer.on_completed()

        return source.subscribe(on_next, on_error, on_completed)
    return AnonymousObservable(subscribe)
