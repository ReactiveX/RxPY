from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.subscription import Subscription

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error


def test_concat_all_subscribes_to_inner_observables_in_order() -> None:
    scheduler = TestScheduler()
    first = scheduler.create_cold_observable(
        on_next(5, 1), on_next(30, 2), on_completed(40)
    )
    second = scheduler.create_cold_observable(on_next(5, 3), on_completed(10))
    outer = scheduler.create_hot_observable(
        on_next(210, first), on_next(220, second), on_completed(225)
    )

    result = scheduler.start(lambda: outer.pipe(ops.concat_all()))

    assert result.messages == [
        on_next(215, 1),
        on_next(240, 2),
        on_next(255, 3),
        on_completed(260),
    ]
    assert outer.subscriptions == [Subscription(200, 225)]
    assert first.subscriptions == [Subscription(210, 250)]
    assert second.subscriptions == [Subscription(250, 260)]


def test_concat_all_inner_error_skips_queued_observables() -> None:
    scheduler = TestScheduler()
    error = Exception("inner failed")
    first = scheduler.create_cold_observable(on_next(5, 1), on_error(20, error))
    second = scheduler.create_cold_observable(on_next(5, 2), on_completed(10))
    outer = scheduler.create_hot_observable(
        on_next(210, first), on_next(215, second), on_completed(220)
    )

    result = scheduler.start(lambda: outer.pipe(ops.concat_all()))

    assert result.messages == [on_next(215, 1), on_error(230, error)]
    assert first.subscriptions == [Subscription(210, 230)]
    assert second.subscriptions == []
