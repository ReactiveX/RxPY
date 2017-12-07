import unittest

from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
        )

        def action(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.send(True)
        scheduler.schedule_absolute(200, action)

        def action1(scheduler, state):
            controller.send(False)
        scheduler.schedule_absolute(205, action1)

        def action2(scheduler, state):
            controller.send(True)
        scheduler.schedule_absolute(209, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
        )

    def test_paused_skips(self):
        subscription = [None]

        scheduler = TestScheduler()

        controller = Subject()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
          )

        def action0(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.send(True)
        scheduler.schedule_absolute(200, action0)


        def action1(scheduler, state):
            controller.send(False)
        scheduler.schedule_absolute(300, action1)

        def action2(scheduler, state):
            controller.send(True)
        scheduler.schedule_absolute(400, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            send(210, 2),
            send(230, 3),
            close(500)
         )

    def test_paused_error(self):
        subscription = [None]

        err = Exception()
        scheduler = TestScheduler()

        controller = Subject()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            throw(230, err),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
        )

        def action0(scheduler, state):
            subscription[0] = xs.pausable(controller).subscribe(results)
            controller.send(True)
        scheduler.schedule_absolute(200, action0)

        def action1(scheduler, state):
            controller.send(False)
        scheduler.schedule_absolute(300, action1)

        def action2(scheduler, state):
            controller.send(True)
        scheduler.schedule_absolute(400, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            send(210, 2),
            throw(230, err)
        )

    def test_paused_with_observable_controller_and_pause_and_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(270, 4),
            send(301, 5),
            send(350, 6),
            send(450, 7),
            close(500)
        )

        controller = scheduler.create_hot_observable(
            send(201, True),
            send(220, False),
            send(250, True)
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
            send(210, 2),
            send(270, 4),
            send(450, 7),
            close(500)
        )
