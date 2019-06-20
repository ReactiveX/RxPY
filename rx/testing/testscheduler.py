from typing import Callable, Any

import rx
from rx.disposable import Disposable
from rx.core import Observable, typing
from rx.scheduler import VirtualTimeScheduler

from .coldobservable import ColdObservable
from .hotobservable import HotObservable
from .mockobserver import MockObserver
from .reactivetest import ReactiveTest


class TestScheduler(VirtualTimeScheduler):
    """Test time scheduler used for testing applications and libraries
    built using Reactive Extensions. All time, both absolute and relative is
    specified as integer ticks"""

    __test__ = False

    def schedule_absolute(self, duetime: typing.AbsoluteTime, action: Callable, state: Any = None) -> typing.Disposable:
        """Schedules an action to be executed at the specified virtual
        time.

        Args:
            duetime: Absolute virtual time at which to execute the
                action.
            action: Action to be executed.
            state: State passed to the action to be executed.

        Returns:
            Disposable object used to cancel the scheduled action
            (best effort).
        """

        duetime = duetime if isinstance(duetime, float) else self.to_seconds(duetime)
        return super().schedule_absolute(duetime, action, state)

    @classmethod
    def add(cls, absolute, relative):
        """Adds a relative virtual time to an absolute virtual time value"""

        return absolute + relative

    def start(self, create=None, created=None, subscribed=None, disposed=None) -> MockObserver:  # type: ignore
        """Starts the test scheduler and uses the specified virtual
        times to invoke the factory function, subscribe to the
        resulting sequence, and dispose the subscription.

        Args:
            create: Factory method to create an observable sequence.
            created: Virtual time at which to invoke the factory to
                create an observable sequence.
            subscribed: Virtual time at which to subscribe to the
                created observable sequence.
            disposed: Virtual time at which to dispose the
            subscription.

        Returns:
            Observer with timestamped recordings of notification
            messages that were received during the virtual time window
            when the subscription to the source sequence was active.
        """

        # Defaults
        create = create or rx.never
        created = created or ReactiveTest.created
        subscribed = subscribed or ReactiveTest.subscribed
        disposed = disposed or ReactiveTest.disposed

        observer = self.create_observer()
        subscription = [None]
        source = [None]

        def action_create(scheduler, state):
            """Called at create time. Defaults to 100"""
            source[0] = create()
            return Disposable()
        self.schedule_absolute(created, action_create)

        def action_subscribe(scheduler, state):
            """Called at subscribe time. Defaults to 200"""
            subscription[0] = source[0].subscribe(observer, scheduler=scheduler)
            return Disposable()
        self.schedule_absolute(subscribed, action_subscribe)

        def action_dispose(scheduler, state):
            """Called at dispose time. Defaults to 1000"""
            subscription[0].dispose()
            return Disposable()
        self.schedule_absolute(disposed, action_dispose)

        super().start()
        return observer

    def create_hot_observable(self, *args) -> Observable:
        """Creates a hot observable using the specified timestamped
        notification messages either as a list or by multiple arguments.

        Args:
            messages: Notifications to surface through the created sequence at
            their specified absolute virtual times.

        Returns hot observable sequence that can be used to assert the timing
        of subscriptions and notifications.
        """

        if args and isinstance(args[0], list):
            messages = args[0]
        else:
            messages = list(args)
        return HotObservable(self, messages)

    def create_cold_observable(self, *args) -> Observable:
        """Creates a cold observable using the specified timestamped
        notification messages either as an array or arguments.

        Args:
            args: Notifications to surface through the created sequence
                at their specified virtual time offsets from the
                sequence subscription time.

        Returns:
            Cold observable sequence that can be used to assert the
            timing of subscriptions and notifications.
        """

        if args and isinstance(args[0], list):
            messages = args[0]
        else:
            messages = list(args)
        return ColdObservable(self, messages)

    def create_observer(self) -> MockObserver:
        """Creates an observer that records received notification messages and
        timestamps those. Return an Observer that can be used to assert the
        timing of received notifications.
        """

        return MockObserver(self)
