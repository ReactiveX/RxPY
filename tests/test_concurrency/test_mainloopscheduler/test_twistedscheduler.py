from datetime import datetime, timedelta
import pytest

twisted = pytest.importorskip("twisted")

from twisted.internet import reactor, defer
from twisted.trial import unittest

from rx.concurrency.mainloopscheduler import TwistedScheduler


class TestTwistedScheduler(unittest.TestCase):

    def test_twisted_schedule_now(self):
        scheduler = TwistedScheduler(reactor)
        res = scheduler.now - datetime.now()

        assert res < timedelta(seconds=1)

    @defer.inlineCallbacks
    def test_twisted_schedule_action(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def done():
            promise.callback('Done')

        scheduler.schedule(action)
        reactor.callLater(0.1, done)

        yield promise
        assert ran is True

    @defer.inlineCallbacks
    def test_twisted_schedule_action_due(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        starttime = reactor.seconds()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = reactor.seconds()

        def done():
            promise.callback('Done')

        scheduler.schedule_relative(0.2, action)
        reactor.callLater(0.3, done)

        yield promise
        diff = endtime - starttime
        assert diff > 0.18

    @defer.inlineCallbacks
    def test_twisted_schedule_action_cancel(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def done():
            promise.callback('Done')

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        reactor.callLater(0.1, done)
        yield promise
        assert ran is False
