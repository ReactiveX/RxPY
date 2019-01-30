from typing import List, Dict

from rx.core.typing import RelativeTime, AbsoluteOrRelativeTime, Scheduler
from rx import Observable
from rx.disposable import CompositeDisposable
from rx.concurrency import NewThreadScheduler

# TODO: hot() should not rely on operators since it could be used for testing
import rx
from rx import operators as ops

# TODO: remove dependency to testing
from rx.testing.recorded import Recorded
from rx.testing.reactivetest import ReactiveTest

new_thread_scheduler = NewThreadScheduler()

# TODO: rename start_time to duetime
# TODO: use a plain impelementation instead of operators
def hot(string: str, timespan: RelativeTime = 0.1, start_time:AbsoluteOrRelativeTime=0,
        lookup: Dict = None, error: Exception = None, scheduler: Scheduler = None) -> Observable:


    scheduler_ = scheduler or new_thread_scheduler

    cold_observable = from_marbles(
        string,
        timespan=timespan,
        lookup=lookup,
        error=error,
        scheduler=scheduler_,
        )
    values = rx.timer(start_time, scheduler=scheduler_).pipe(
        ops.flat_map(lambda _: cold_observable),
        ops.publish(),
        )

    values.connect()
    return values


def from_marbles(string: str, timespan: RelativeTime = 0.1, lookup: Dict = None,
                 error: Exception = None, scheduler: Scheduler = None) -> Observable:
    """Convert a marble diagram string to a cold observable sequence, using
    an optional scheduler to enumerate the events.

    Each character in the string will advance time by timespan
    (exept for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. Digit 0-9 will be cast
    to int.

    Special characters:
        +--------+--------------------------------------------------------+
        |  `-`   | advance time by timespan                               |
        +--------+--------------------------------------------------------+
        |  `#`   | on_error()                                             |
        +--------+--------------------------------------------------------+
        |  `|`   | on_completed()                                         |
        +--------+--------------------------------------------------------+
        |  `(`   | open a group of marbles sharing the same timestamp     |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of marbles                               |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time.|
        +--------+--------------------------------------------------------+

    In a group of marbles, the position of the initial `(` determines the
    timestamp at which grouped marbles will be emitted. E.g. `--(abc)--` will
    emit a, b, c at 2 * timespan and then advance virtual time by 5 * timespan.

    Examples:
        >>> from_marbles("--1--(42)-3--|")
        >>> from_marbles("a--B--c-", lookup={'a': 1, 'B': 2, 'c': 3})
        >>> from_marbles("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.

        lookup: [Optional] dict used to convert a marble into a specified
            value. If not specified, defaults to {}.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

        scheduler: [Optional] Scheduler to run the the input sequence
            on.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    disp = CompositeDisposable()
    records = parse(string, timespan=timespan, lookup=lookup, error=error)

    def schedule_msg(record, observer, scheduler):
        timespan = record.time
        notification = record.value

        def action(scheduler, state=None):
            notification.accept(observer)

        disp.add(scheduler.schedule_relative(timespan, action))

    def subscribe(observer, scheduler_):
        _scheduler = scheduler or scheduler_ or new_thread_scheduler

        for record in records:
            # Don't make closures within a loop
            schedule_msg(record, observer, _scheduler)
        return disp
    return Observable(subscribe)


def to_marbles(scheduler=None, timespan=0.1):
    """Convert an observable sequence into a marble diagram string

    Args:
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Observable stream.
    """
    def _to_marbles(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            scheduler = scheduler or new_thread_scheduler

            result: List[str] = []
            last = scheduler.now

            def add_timespan():
                nonlocal last

                now = scheduler.now
                diff = now - last
                last = now
                secs = scheduler.to_seconds(diff)
                dashes = "-" * int((secs + timespan / 2.0) * (1.0 / timespan))
                result.append(dashes)

            def on_next(value):
                add_timespan()
                result.append(stringify(value))

            def on_error(exception):
                add_timespan()
                result.append(stringify(exception))
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            def on_completed():
                add_timespan()
                result.append("|")
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            return source.subscribe_(on_next, on_error, on_completed)
        return Observable(subscribe)
    return _to_marbles


def stringify(value):
    """Utility for stringifying an event.
    """
    string = str(value)
    if len(string) > 1:
        string = "(%s)" % string

    return string

# TODO: remove support of subscription symbol ^
# TODO: consecutive characters should be considered as one element
# TODO: add support of comma , to split elements in group
def parse(string: str, timespan: RelativeTime = 1, time_shift: AbsoluteOrRelativeTime = 0,
          lookup: Dict = None, error: Exception = None) -> List[Recorded]:
    """Convert a marble diagram string to a list of records of type
    :class:`rx.testing.recorded.Recorded`.

    Each character in the string will advance time by timespan
    (exept for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted according to their horizontal
    position in the diagram. Digit 0-9 will be cast to :class:`int`.

    Special characters:
        +--------+--------------------------------------------------------+
        |  `-`   | advance time by timespan                               |
        +--------+--------------------------------------------------------+
        |  `#`   | on_error()                                             |
        +--------+--------------------------------------------------------+
        |  `|`   | on_completed()                                         |
        +--------+--------------------------------------------------------+
        |  `(`   | open a group of marbles sharing the same timestamp     |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of marbles                               |
        +--------+--------------------------------------------------------+
        |  `^`   | subscription (hot observable only)                     |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time.|
        +--------+--------------------------------------------------------+

    In a group of marbles, the position of the initial `(` determines the
    timestamp at which grouped marbles will be emitted. E.g. `--(abc)--` will
    emit a, b, c at 2 * timespan and then advance virtual time by 5 * timespan.

    If a subscription symbol `^` is specified (hot observable), each marble
    will be emitted at a time relative to their position from the '^'symbol.
    E.g. if subscription time is set to 0, Every marbles
    that appears before the `^` will have negative timestamp.

    Examples:
        >>> res = parse("1-2-3-|")
        >>> res = parse("--1--^-(42)-3--|")
        >>> res = parse("a--B---c-", lookup={'a': 1, 'B': 2, 'c': 3})

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character.
            Default set to 1.

        lookup: [Optional] dict used to convert a marble into a specified
            value. If not specified, defaults to {}.

        time_shift: [Optional] absolute time of subscription.
            If not specified, defaults to 0.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

    Returns:
        A list of records of type :class:`rx.testing.recorded.Recorded`
        containing time and :class:`Notification` as value.
    """

    error = error or Exception('error')
    lookup = lookup or {}

    string = string.replace(' ', '')

    isub = string.find('^')
    if isub > 0:
        time_shift -= isub * timespan

    records = []
    group_frame = 0
    in_group = False
    has_subscribe = False

    def check_group_opening():
        if in_group:
            raise ValueError(
                "A group of items must be closed before opening a new one. "
                'Got "{}..."'.format(string[:char_frame+1]))

    def check_group_closing():
        if not in_group:
            raise ValueError(
                "A Group of items have already been closed before. "
                "Got {} ...".format(string[:char_frame+1]))

    def check_subscription():
        if has_subscribe:
            raise ValueError(
                "Only one subscription is allowed for a hot observable. "
                "Got {} ...".format(string[:char_frame+1]))

    def shift(frame):
        return frame + time_shift

    for i, char in enumerate(string):
        char_frame = i * timespan

        if char == '(':
            check_group_opening()
            in_group = True
            group_frame = char_frame

        elif char == ')':
            check_group_closing()
            in_group = False

        elif char == '-':
            pass

        elif char == '|':
            frame = group_frame if in_group else char_frame
            record = ReactiveTest.on_completed(shift(frame))
            records.append(record)

        elif char == '#':
            frame = group_frame if in_group else char_frame
            record = ReactiveTest.on_error(shift(frame), error)
            records.append(record)

        elif char == '^':
            check_subscription()

        else:
            frame = group_frame if in_group else char_frame
            try:
                char = int(char)
            except ValueError:
                pass
            value = lookup.get(char, char)
            record = ReactiveTest.on_next(shift(frame), value)
            records.append(record)

    if in_group:
        raise ValueError(
            "The last group of items has been opened but never closed. "
            "Missing a ')."
            )

    return records

