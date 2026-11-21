import unittest
from concurrent.futures import Future

import pytest

import reactivex
from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.scheduler import ImmediateScheduler
from reactivex.subject import BehaviorSubject, Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


class TestTakeUntil(unittest.TestCase):
    def test_take_until_preempt_somedata_next(self):
        scheduler = TestScheduler()
        left_msgs = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]
        right_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
        left = scheduler.create_hot_observable(left_msgs)
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_next(220, 3), on_completed(225)]

    def test_take_until_preempt_somedata_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        left_msgs = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]
        right_msgs = [on_next(150, 1), on_error(225, ex)]
        left = scheduler.create_hot_observable(left_msgs)
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_next(220, 3), on_error(225, ex)]

    def test_take_until_nopreempt_somedata_empty(self):
        scheduler = TestScheduler()
        left_msgs = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]
        right_msgs = [on_next(150, 1), on_completed(225)]
        left = scheduler.create_hot_observable(left_msgs)
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]

    def test_take_until_nopreempt_somedata_never(self):
        scheduler = TestScheduler()
        left_msgs = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]
        left = scheduler.create_hot_observable(left_msgs)
        right = reactivex.never()

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(210, 2),
            on_next(220, 3),
            on_next(230, 4),
            on_next(240, 5),
            on_completed(250),
        ]

    def test_take_until_preempt_never_next(self):
        scheduler = TestScheduler()
        right_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
        left = reactivex.never()
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [on_completed(225)]

    def test_take_until_preempt_never_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        right_msgs = [on_next(150, 1), on_error(225, ex)]
        left = reactivex.never()
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [on_error(225, ex)]

    def test_take_until_nopreempt_never_empty(self):
        scheduler = TestScheduler()
        right_msgs = [on_next(150, 1), on_completed(225)]
        left = reactivex.never()
        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == []

    def test_take_until_nopreempt_never_never(self):
        scheduler = TestScheduler()
        left = reactivex.never()
        right = reactivex.never()

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == []

    def test_take_until_preempt_beforefirstproduced(self):
        scheduler = TestScheduler()
        left_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
        right_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        left = scheduler.create_hot_observable(left_msgs)
        r = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(r))

        results = scheduler.start(create)
        assert results.messages == [on_completed(210)]

    def test_take_until_preempt_beforefirstproduced_remain_silent_and_proper_disposed(
        self,
    ):
        scheduler = TestScheduler()
        left_msgs = [on_next(150, 1), on_error(215, "ex"), on_completed(240)]
        right_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        source_not_disposed = [False]

        def action(_):
            source_not_disposed[0] = True

        left = scheduler.create_hot_observable(left_msgs).pipe(
            ops.do_action(on_next=action)
        )

        right = scheduler.create_hot_observable(right_msgs)

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)

        assert results.messages == [on_completed(210)]
        assert not source_not_disposed[0]

    def test_take_until_nopreempt_afterlastproduced_proper_disposed_signal(self):
        scheduler = TestScheduler()
        left_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
        right_msgs = [on_next(150, 1), on_next(250, 2), on_completed(260)]
        signal_not_disposed = [False]
        left = scheduler.create_hot_observable(left_msgs)

        def action(_):
            signal_not_disposed[0] = True

        right = scheduler.create_hot_observable(right_msgs).pipe(
            ops.do_action(on_next=action)
        )

        def create():
            return left.pipe(ops.take_until(right))

        results = scheduler.start(create)
        assert results.messages == [on_next(230, 2), on_completed(240)]
        assert not signal_not_disposed[0]


@pytest.mark.parametrize("scheduler", [None, ImmediateScheduler.singleton()])
@pytest.mark.parametrize("signal", ["value", "error", "future"])
def test_take_until_synchronous_signal_does_not_subscribe_source(
    scheduler: abc.SchedulerBase | None, signal: str
) -> None:
    subscriptions: list[abc.SchedulerBase] = []
    values: list[int] = []
    errors: list[Exception] = []
    completed: list[bool] = []
    error = ValueError("stop failed")

    def factory(actual_scheduler: abc.SchedulerBase) -> Observable[int]:
        subscriptions.append(actual_scheduler)
        return reactivex.of(1, 2, 3)

    notifier: Observable[int] | Future[int]
    if signal == "value":
        notifier = BehaviorSubject(0)
    elif signal == "error":
        notifier = reactivex.throw(error, scheduler=ImmediateScheduler.singleton())
    else:
        notifier = Future()
        notifier.set_result(0)

    reactivex.defer(factory).pipe(ops.take_until(notifier)).subscribe(
        values.append,
        errors.append,
        lambda: completed.append(True),
        scheduler=scheduler,
    )

    assert subscriptions == []
    assert values == []
    assert errors == ([error] if signal == "error" else [])
    assert completed == ([] if signal == "error" else [True])
    if isinstance(notifier, BehaviorSubject):
        assert not notifier.observers


@pytest.mark.parametrize("scheduler", [None, ImmediateScheduler.singleton()])
def test_take_until_synchronous_notifier_completion_allows_source(
    scheduler: abc.SchedulerBase | None,
) -> None:
    values: list[int] = []
    completed: list[bool] = []

    reactivex.of(1, 2, 3).pipe(ops.take_until(reactivex.empty())).subscribe(
        values.append, on_completed=lambda: completed.append(True), scheduler=scheduler
    )

    assert values == [1, 2, 3]
    assert completed == [True]


def test_take_until_notifier_observes_source_subscription_side_effects() -> None:
    notifier = Subject[int]()
    values: list[int] = []
    completed: list[bool] = []

    def factory(scheduler: abc.SchedulerBase) -> Observable[int]:
        notifier.on_next(0)
        return reactivex.of(1, 2, 3)

    reactivex.defer(factory).pipe(ops.take_until(notifier)).subscribe(
        values.append, on_completed=lambda: completed.append(True)
    )

    assert values == []
    assert completed == [True]
    assert not notifier.observers


@pytest.mark.parametrize("source_errors", [False, True])
def test_take_until_disposes_notifier_when_source_terminates(
    source_errors: bool,
) -> None:
    source = Subject[int]()
    notifier = Subject[int]()
    error = ValueError("source failed")
    errors: list[Exception] = []
    completed: list[bool] = []

    source.pipe(ops.take_until(notifier)).subscribe(
        on_error=errors.append, on_completed=lambda: completed.append(True)
    )
    assert len(source.observers) == len(notifier.observers) == 1

    if source_errors:
        source.on_error(error)
    else:
        source.on_completed()

    assert errors == ([error] if source_errors else [])
    assert completed == ([] if source_errors else [True])
    assert not source.observers
    assert not notifier.observers


def test_take_until_disposal_unsubscribes_both_sources() -> None:
    source = Subject[int]()
    notifier = Subject[int]()
    subscription = source.pipe(ops.take_until(notifier)).subscribe()
    assert len(source.observers) == len(notifier.observers) == 1

    subscription.dispose()

    assert not source.observers
    assert not notifier.observers
