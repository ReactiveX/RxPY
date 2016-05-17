import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def is_even(num):
    return +num % 2 == 0


class TestPartition(unittest.TestCase):
    def test_partition_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_completed(210)
        )

        subscription1 = [None]
        subscription2 = [None]
        observables = []

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()
        results1.messages.assert_equal(
            on_completed(210)
        )

        results2.messages.assert_equal(
            on_completed(210)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 210)
        )

    def test_partition_single(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_completed(220)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4),
            on_completed(220)
        )

        results2.messages.assert_equal(
            on_completed(220)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 220)
        )

    def test_partition_each(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(220, 3),
            on_completed(230)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4),
            on_completed(230)
        )

        results2.messages.assert_equal(
            on_next(220, 3),
            on_completed(230)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 230)
        )

    def test_partition_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1),
            on_completed(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4),
            on_next(290, 2),
            on_completed(360)
        )

        results2.messages.assert_equal(
            on_next(240, 3),
            on_next(350, 1),
            on_completed(360)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 360)
        )

    def test_partition_not_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4),
            on_next(290, 2)
        )

        results2.messages.assert_equal(
            on_next(240, 3),
            on_next(350, 1)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

    def test_partition_error(self):
        error = Exception()
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_error(290, error),
            on_next(350, 1),
            on_completed(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4),
            on_error(290, error)
        )

        results2.messages.assert_equal(
            on_next(240, 3),
            on_error(290, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 290)
        )

    def test_partition_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1),
            on_completed(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(280, action2)

        scheduler.start()

        results1.messages.assert_equal(
            on_next(210, 4)
        )

        results2.messages.assert_equal(
            on_next(240, 3)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 280)
        )
