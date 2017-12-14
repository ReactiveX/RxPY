import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.subjects import Subject

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)
        )

        def action0(scheduler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
            controller.send(True)
        scheduler.schedule_absolute(200, action0)

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

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            close(500)]

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

        def action0(schedler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
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

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(400, 4),
            send(400, 5),
            send(400, 6),
            close(500)]

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
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
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

        assert results.messages == [
        send(210, 2),
            throw(230, err)]

    def test_paused_skip_initial_elements(self):
        subscription = [None]
        scheduler = TestScheduler()

        controller = Subject()
        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(230, 2),
            send(270, 3),
            close(400)
        )

        def action1(scheduler, state):
            subscription[0] = xs.pausable_buffered(controller).subscribe(results)
            controller.send(False)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            controller.send(True)
        scheduler.schedule_absolute(280, action2)

        def action3(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(1000, action3)

        scheduler.start()
        assert results.messages == [
            send(280, 2),
            send(280, 3),
            close(400)]

    def test_paused_with_observable_controller_and_pause_and_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            send(450, 7),
            send(470, 8),
            close(500)
         )

        controller = scheduler.create_hot_observable(
            send(201, True),
            send(300, False),
            send(400, True)
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

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(400, 4),
            send(400, 5),
            send(400, 6),
            send(450, 7),
            send(480, 8),
            close(500)]

    def test_paused_with_immediate_unpause(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            close(500)
        )

        controller = Observable.just(True)

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            subscription[0] = pausable_buffered.subscribe(results)
        scheduler.schedule_absolute(200, action1)

        scheduler.start()

        assert results.messages == [
            send(210, 2),
            close(500)]

    def test_paused_when_finishing(self):
        subscription = [None]

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            send(450, 7),
            send(470, 8),
            close(500)
        )

        controller = scheduler.create_hot_observable(
            send(201, True),
            send(300, False),
            send(400, True)
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

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(400, 4),
            send(400, 5),
            send(400, 6),
            send(450, 7)]

    def test_paused_with_observable_controller_and_pause_and_unpause_after_end(self):
        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            send(450, 7),
            send(470, 8),
            close(500)
          )

        controller = scheduler.create_hot_observable(
            send(201, True),
            send(300, False),
            send(600, True)
        )

        def create():
            return xs.pausable_buffered(controller)
        results = scheduler.start(create)

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(600, 4),
            send(600, 5),
            send(600, 6),
            send(600, 7),
            send(600, 8),
            close(600)]

    def test_paused_with_observable_controller_and_pause_and_unpause_after_error(self):
        error = Exception()

        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(230, 3),
            send(301, 4),
            send(350, 5),
            send(399, 6),
            send(450, 7),
            send(470, 8),
            throw(500, error)
        )

        controller = scheduler.create_hot_observable(
            send(201, True),
            send(300, False),
            send(600, True)
        )

        def create():
            return xs.pausable_buffered(controller)

        results = scheduler.start(create=create)

        assert results.messages == [
            send(210, 2),
            send(230, 3),
            send(600, 4),
            send(600, 5),
            send(600, 6),
            send(600, 7),
            send(600, 8),
            throw(600, error)]

    def test_paused_with_state_change_in_subscriber(self):
        scheduler = TestScheduler()

        results = scheduler.create_observer()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(250, 3),
            send(270, 4),
            send(330, 5),
            close(500)
        )

        controller = Subject()

        pausable_buffered = xs.pausable_buffered(controller)

        def action1(scheduler, state):
            def send(value):
                results.send(value)
                controller.send(False)

                def action2(scheduler, state):
                    controller.send(True)
                scheduler.schedule_relative(100, action2)

            subscription = pausable_buffered.subscribe_callbacks(send, results.throw, results.close)
            controller.send(True)

        scheduler.schedule_absolute(200, action1)

        scheduler.start()

        assert results.messages == [
            send(210, 2),
            send(310, 3),
            send(310, 4),
            send(410, 5),
            close(500)]
