import unittest

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject
from rx.backpressure.controlledsubject import ControlledSubject
from rx.backpressure.windowedobservable import WindowedObservable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWindowedObservable(unittest.TestCase):
    def test_windowedobservalbe_simple(self):
        scheduler = TestScheduler()
        windowed = [None]
        subject = [None]
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
            subject[0] = ControlledSubject(enable_queue=False, scheduler=scheduler)
            xs.subscribe(subject[0])
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state=None):
            windowed[0] = WindowedObservable(subject[0], 2, scheduler=scheduler)
        scheduler.schedule_absolute(120, action2)

        def action3(scheduler, state=None):
            windowed[0].subscribe(results1)
        scheduler.schedule_absolute(220, action3)

        def action4(scheduler, state=None):
            windowed[0].subscribe(results2)
        scheduler.schedule_absolute(355, action4)

        scheduler.start()
        results1.messages.assert_equal(
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
        )

        results2.messages.assert_equal(
            on_next(399, 6),
            on_completed(500)
        )
