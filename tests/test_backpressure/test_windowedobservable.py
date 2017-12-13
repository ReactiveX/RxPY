import unittest

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject
from rx.backpressure.controlledsubject import ControlledSubject
from rx.backpressure.windowedobservable import WindowedObservable

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
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
        assert results1.messages == [
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)]

        assert results2.messages == [
            send(399, 6),
            close(500)]
