import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestControlledObservable(unittest.TestCase):
    def test_controlledobservable_simple(self):
        scheduler = TestScheduler()
        controlled = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
        )

        def action1(scheduler, state=None):
            controlled[0] = xs.controlled(scheduler=scheduler)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state=None):
            controlled[0].subscribe(results1)
        scheduler.schedule_absolute(300, action2)

        def action3(scheduler, state=None):
            controlled[0].request(2)
        scheduler.schedule_absolute(380, action3)

        def action4(scheduler, state=None):
            controlled[0].subscribe(results2)
        scheduler.schedule_absolute(400, action4)

        def action3(scheduler, state=None):
           controlled[0].request(1)
        scheduler.schedule_absolute(410, action3)

        scheduler.start()
        assert results1.messages == [
            send(380, 4),
            send(380, 5),
            send(410, 6),
            close(500)]

        assert results2.messages == [
            send(410, 6),
            close(500)]
