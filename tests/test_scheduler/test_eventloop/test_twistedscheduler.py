from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.scheduler.eventloop import TwistedScheduler

twisted: Any = pytest.importorskip("twisted")
defer: Any = pytest.importorskip("twisted.internet.defer")
reactor: Any = pytest.importorskip("twisted.internet.reactor")
unittest: Any = pytest.importorskip("twisted.trial.unittest")


class TestTwistedScheduler(unittest.TestCase):
    def test_twisted_schedule_now(self) -> None:
        scheduler = TwistedScheduler(reactor)
        diff = scheduler.now - datetime.now(UTC)
        assert abs(diff) < timedelta(milliseconds=100)

    def test_twisted_schedule_now_units(self) -> None:
        scheduler = TwistedScheduler(reactor)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    @defer.inlineCallbacks  # pyright: ignore[reportUntypedFunctionDecorator]
    def test_twisted_schedule_action(self) -> Generator[Any, Any, None]:
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        def done() -> None:
            promise.callback("Done")

        scheduler.schedule(action)
        reactor.callLater(0.1, done)

        yield promise
        assert ran is True

    @defer.inlineCallbacks  # pyright: ignore[reportUntypedFunctionDecorator]
    def test_twisted_schedule_action_due(self) -> Generator[Any, Any, None]:
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        starttime = reactor.seconds()
        endtime = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = reactor.seconds()

        def done() -> None:
            promise.callback("Done")

        scheduler.schedule_relative(0.2, action)
        reactor.callLater(0.3, done)

        yield promise
        diff = endtime - starttime
        assert diff > 0.18

    @defer.inlineCallbacks  # pyright: ignore[reportUntypedFunctionDecorator]
    def test_twisted_schedule_action_absolute(self) -> Generator[Any, Any, None]:
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        def done() -> None:
            promise.callback("Done")

        duetime = datetime.now(UTC) + timedelta(milliseconds=100)
        scheduler.schedule_absolute(duetime, action)
        reactor.callLater(0.3, done)

        yield promise
        assert ran is True

    @defer.inlineCallbacks  # pyright: ignore[reportUntypedFunctionDecorator]
    def test_twisted_schedule_action_cancel(self) -> Generator[Any, Any, None]:
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        def done() -> None:
            promise.callback("Done")

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        reactor.callLater(0.1, done)
        yield promise
        assert ran is False
