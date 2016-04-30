from datetime import datetime, timedelta

from nose import SkipTest
try:
    import twisted
except ImportError:
    raise SkipTest("Twisted not installed")

from twisted.internet import reactor, defer
from twisted.trial import unittest

from rx.concurrency import TwistedScheduler


class TestTwistedScheduler(unittest.TestCase):

    def test_twisted_schedule_now(self):
        scheduler = TwistedScheduler(reactor)
        res = scheduler.now - datetime.now()
        assert(res < timedelta(seconds=1))

    @defer.inlineCallbacks
    def test_twisted_schedule_action(self):
        scheduler = TwistedScheduler(reactor)
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        disposable = scheduler.schedule(action)

        promise = defer.Deferred()
        def done():
            assert(ran[0] is True)
            promise.callback("Done")
        reactor.callLater(0.1, done)
        yield promise

    @defer.inlineCallbacks
    def test_twisted_schedule_action_due(self):
        scheduler = TwistedScheduler(reactor)
        starttime = reactor.seconds()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = reactor.seconds()

        scheduler.schedule_relative(200, action)

        promise = defer.Deferred()
        def done():
            diff = endtime[0]-starttime
            assert(diff > 0.18)
            promise.callback("Done")
        reactor.callLater(0.3, done)
        yield promise

    @defer.inlineCallbacks
    def test_twisted_schedule_action_cancel(self):
        ran = [False]
        scheduler = TwistedScheduler(reactor)

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(10, action)
        d.dispose()

        promise = defer.Deferred()
        def done():
            assert(not ran[0])
            promise.callback("Done")
        reactor.callLater(0.1, done)

        yield promise
