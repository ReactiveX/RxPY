import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
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
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
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
        results1.messages.assert_equal(
            on_next(381, 4),
            on_next(381, 5),
            on_next(411, 6),
            on_completed(500)
        )

        results2.messages.assert_equal(
            on_next(411, 6),
            on_completed(500)
        )
