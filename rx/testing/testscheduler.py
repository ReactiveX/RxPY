import logging
from datetime import datetime, timedelta

from rx import Observable
from rx.concurrency import VirtualTimeScheduler
from rx.disposables import Disposable

from .coldobservable import ColdObservable
from .hotobservable import HotObservable
from .mockobserver import MockObserver
from .reactivetest import ReactiveTest

log = logging.getLogger("Rx")

class TestScheduler(VirtualTimeScheduler):
    """Virtual time scheduler used for testing applications and libraries
    built using Reactive Extensions."""

    def __init__(self):
        def comparer(a, b):
            return a - b
        super(TestScheduler, self).__init__(0, comparer)

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at the specified virtual time.

        Keyword arguments:
        duetime -- Absolute virtual time at which to execute the action.
        action -- Action to be executed.
        state -- State passed to the action to be executed.

        Returns disposable object used to cancel the scheduled action (best effort).
        """

        log.debug("TestScheduler.schedule_absolute(duetime=%s, state=%s)" % (duetime, state))

        duetime = duetime if isinstance(duetime, int) else self.to_relative(duetime)

        if duetime <= self.clock:
            duetime = self.clock + 1

        return super(TestScheduler, self).schedule_absolute(duetime, action, state)

    def add(self, absolute, relative):
        log.debug("TestScheduler.add(absolute=%s, relative=%s)" % (absolute, relative))
        return absolute + relative

    @classmethod
    def to_datetime_offset(cls, absolute):
        """Converts the absolute virtual time value to a DateTimeOffset value.

        Keyword arguments:
        absolute -- Absolute virtual time value to convert.

        Returns corresponding DateTimeOffset value.
        """

        return datetime.fromtimestamp(absolute/1000.0)

    @classmethod
    def to_relative(cls, timespan):
        """Converts timespan to from datetime/timedelta to milliseconds"""

        if isinstance(timespan, datetime):
            timespan = timespan - datetime.fromtimestamp(0)
        if isinstance(timespan, timedelta):
            timespan = int(timespan.total_seconds()*1000)
        return timespan

    def start(self, create=None, created=None, subscribed=None, disposed=None):
        """Starts the test scheduler and uses the specified virtual times to
        invoke the factory function, subscribe to the resulting sequence, and
        dispose the subscription.

        Keyword arguments:
        create -- Factory method to create an observable sequence.
        created -- Virtual time at which to invoke the factory to create an observable sequence.
        subscribed -- Virtual time at which to subscribe to the created observable sequence.
        disposed -- Virtual time at which to dispose the subscription.

        Returns Observer with timestamped recordings of notification messages
        that were received during the virtual time window when the subscription
        to the source sequence was active.
        """

        # Defaults
        create = create or Observable.empty
        created = created or ReactiveTest.created
        subscribed = subscribed or ReactiveTest.subscribed
        disposed= disposed or ReactiveTest.disposed

        observer = self.create_observer()
        subscription = [None]
        source = [None]

        def action_create(scheduler, state):
            """Called at create time. Defaults to 100"""
            source[0] = create()
            return Disposable.empty()
        self.schedule_absolute(created, action_create)

        def action_subscribe(scheduler, state):
            """Called at subscribe time. Defaults to 200"""
            subscription[0] = source[0].subscribe(observer)
            return Disposable.empty()
        self.schedule_absolute(subscribed, action_subscribe)

        def action_dispose(scheduler, state):
            """Called at dispose time. Defaults to 1000"""
            subscription[0].dispose()
            return Disposable.empty()
        self.schedule_absolute(disposed, action_dispose)

        super(TestScheduler, self).start()
        return observer

    def create_hot_observable(self, *args):
        """Creates a hot observable using the specified timestamped
        notification messages either as an array or arguments.

        Keyword arguments:
        messages -- Notifications to surface through the created sequence at
            their specified absolute virtual times.

        Returns hot observable sequence that can be used to assert the timing
        of subscriptions and notifications.
        """

        if len(args) and isinstance(args[0], list):
            messages = args[0]
        else:
            messages = list(args)
        return HotObservable(self, messages)

    def create_cold_observable(self, *args):
        """Creates a cold observable using the specified timestamped
        notification messages either as an array or arguments.

        Keyword arguments:
        messages -- Notifications to surface through the created sequence at
            their specified virtual time offsets from the sequence subscription
            time.

        Returns cold observable sequence that can be used to assert the timing
        of subscriptions and notifications.
        """

        if len(args) and isinstance(args[0], list):
            messages = args[0]
        else:
            messages = list(args)
        return ColdObservable(self, messages)

    def create_observer(self):
        """Creates an observer that records received notification messages and
        timestamps those. Return an Observer that can be used to assert the
        timing of received notifications.
        """

        return MockObserver(self)

