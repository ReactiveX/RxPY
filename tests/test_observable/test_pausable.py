import unittest

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestPausable(unittest.TestCase):
    def test_paused_no_skip(self):
        subscription = [None]

        scheduler = TestScheduler()
        controller = Subject()
        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
        )

        def action(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.on_next(True)
        scheduler.schedule_absolute(200, action)

        def action1(scheduler, state):
            controller.on_next(False)
        scheduler.schedule_absolute(205, action1)

        def action2(scheduler, state):
            controller.on_next(True)
        scheduler.schedule_absolute(209, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
        )

    def test_paused_skips(self):
        subscription = [None]

        scheduler = TestScheduler()

        controller = Subject()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
          )

        def action0(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.on_next(True)
        scheduler.schedule_absolute(200, action0)


        def action1(scheduler, state):
            controller.on_next(False)
        scheduler.schedule_absolute(300, action1)

        def action2(scheduler, state):
            controller.on_next(True)
        scheduler.schedule_absolute(400, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_completed(500)
         )

    def test_paused_error(self):
        subscription = [None]

        err = Exception()
        scheduler = TestScheduler()

        controller = Subject()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_error(230, err),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_completed(500)
        )

        def action0(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.on_next(True)
        scheduler.schedule_absolute(200, action0)

        def action1(scheduler, state):
            controller.on_next(False)
        scheduler.schedule_absolute(300, action1)

        def action2(scheduler, state):
            controller.on_next(True)
        scheduler.schedule_absolute(400, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_error(230, err)
        )

    def test_paused_with_observable_controller_and_pause_and_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(270, 4),
            on_next(301, 5),
            on_next(350, 6),
            on_next(450, 7),
            on_completed(500)
        )

        controller = scheduler.create_hot_observable(
            on_next(201, True),
            on_next(220, False),
            on_next(250, True)
        )

        pausable = xs.pausable(controller)

        def action1(scheduler, state):
            subscription[0] = pausable.subscribe(results)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            pausable.pause()
        scheduler.schedule_absolute(300, action2)

        def action3(scheduler, state):
            pausable.resume()
        scheduler.schedule_absolute(400, action3)

        def action4(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action4)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(270, 4),
            on_next(450, 7),
            on_completed(500)
        )
