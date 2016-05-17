import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestPausable_buffered(unittest.TestCase):

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

        def action0(scheduler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
            controller.on_next(True)
        scheduler.schedule_absolute(200, action0)

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

        def action0(schedler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
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
            on_next(400, 4),
            on_next(400, 5),
            on_next(400, 6),
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
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
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

    def test_paused_skip_initial_elements(self):
        subscription = [None]
        scheduler = TestScheduler()

        controller = Subject()
        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(230, 2),
            on_next(270, 3),
            on_completed(400)
        )

        def action1(scheduler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
            controller.on_next(False)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            controller.on_next(True)
        scheduler.schedule_absolute(280, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()
        results.messages.assert_equal(
            on_next(280, 2),
            on_next(280, 3),
            on_completed(400)
        )

    def test_paused_with_observable_controller_and_pause_and_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_next(450, 7),
            on_next(470, 8),
            on_completed(500)
         )

        controller = scheduler.create_hot_observable(
            on_next(201, True),
            on_next(300, False),
            on_next(400, True)
        )

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            subscription[0] = pausable_buffered.subscribe(results)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            pausable_buffered.pause()
        scheduler.schedule_absolute(460, action2)

        def action3(scheduler, state):
            pausable_buffered.resume()
        scheduler.schedule_absolute(480, action3)

        def action4(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action4)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_next(400, 4),
            on_next(400, 5),
            on_next(400, 6),
            on_next(450, 7),
            on_next(480, 8),
            on_completed(500)
        )

    def test_paused_with_immediate_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_completed(500)
        )

        controller = Observable.just(True)

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            subscription[0] = pausable_buffered.subscribe(results)
        scheduler.schedule_absolute(200, action1)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_completed(500)
        )

    def test_paused_when_finishing(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_next(450, 7),
            on_next(470, 8),
            on_completed(500)
        )

        controller = scheduler.create_hot_observable(
            on_next(201, True),
            on_next(300, False),
            on_next(400, True)
        )

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            subscription[0] = pausable_buffered.subscribe(results)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            pausable_buffered.pause()
        scheduler.schedule_absolute(460, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_next(400, 4),
            on_next(400, 5),
            on_next(400, 6),
            on_next(450, 7)
        )

    def test_paused_with_observable_controller_and_pause_and_unpause_after_end(self):
        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_next(450, 7),
            on_next(470, 8),
            on_completed(500)
          )

        controller = scheduler.create_hot_observable(
            on_next(201, True),
            on_next(300, False),
            on_next(600, True)
        )

        def create():
            return xs.pausable_buffered(controller)
        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_next(600, 4),
            on_next(600, 5),
            on_next(600, 6),
            on_next(600, 7),
            on_next(600, 8),
            on_completed(600)
        )

    def test_paused_with_observable_controller_and_pause_and_unpause_after_error(self):
        error = Exception()

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(230, 3),
            on_next(301, 4),
            on_next(350, 5),
            on_next(399, 6),
            on_next(450, 7),
            on_next(470, 8),
            on_error(500, error)
        )

        controller = scheduler.create_hot_observable(
            on_next(201, True),
            on_next(300, False),
            on_next(600, True)
        )

        def create():
            return xs.pausable_buffered(controller)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(230, 3),
            on_next(600, 4),
            on_next(600, 5),
            on_next(600, 6),
            on_next(600, 7),
            on_next(600, 8),
            on_error(600, error)
        )

    def test_paused_with_state_change_in_subscriber(self):
        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(250, 3),
            on_next(270, 4),
            on_next(330, 5),
            on_completed(500)
        )

        controller = Subject()

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            def on_next(value):
                results.on_next(value)
                controller.on_next(False)

                def action2(scheduler, state):
                    controller.on_next(True)
                scheduler.schedule_relative(100, action2)

            subscription = pausable_buffered.subscribe(on_next, results.on_error, results.on_completed)
            controller.on_next(True)

        scheduler.schedule_absolute(200, action1)

        scheduler.start()

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(310, 3),
            on_next(310, 4),
            on_next(410, 5),
            on_completed(500)
        )
