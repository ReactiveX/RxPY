import pytest

import reactivex
from reactivex import Observable
from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_error = ReactiveTest.on_error
on_completed = ReactiveTest.on_completed
subscribe = ReactiveTest.subscribe


def recover(
    kind: str, first: Observable[int], second: Observable[int]
) -> Observable[int]:
    if kind == "catch":
        return reactivex.catch(first, second)
    if kind == "catch_iterable":
        return reactivex.catch_with_iterable([first, second])
    if kind == "resume":
        return reactivex.on_error_resume_next(first, second)
    return first.pipe(ops.on_error_resume_next(second))


@pytest.mark.parametrize(
    "kind", ["catch", "catch_iterable", "resume", "resume_operator"]
)
def test_recovery_repeat_restarts_sources(kind: str) -> None:
    values: list[int] = []
    source = recover(kind, reactivex.throw(ValueError("first")), reactivex.just(2))
    source.pipe(ops.repeat(2)).subscribe(values.append)
    assert values == [2, 2]


@pytest.mark.parametrize(
    "kind", ["catch", "catch_iterable", "resume", "resume_operator"]
)
def test_recovery_overlapping_subscriptions_have_independent_sources(kind: str) -> None:
    scheduler = TestScheduler()
    first = scheduler.create_cold_observable(
        on_next(10, 1), on_error(20, ValueError("first"))
    )
    second = scheduler.create_cold_observable(on_next(10, 2), on_completed(20))
    source = recover(kind, first, second)
    one = scheduler.create_observer()
    two = scheduler.create_observer()
    source.subscribe(one, scheduler=scheduler)
    scheduler.advance_to(5)
    source.subscribe(two, scheduler=scheduler)
    scheduler.advance_to(100)
    assert one.messages == [on_next(10, 1), on_next(30, 2), on_completed(40)]
    assert two.messages == [on_next(15, 1), on_next(35, 2), on_completed(45)]
    assert first.subscriptions == [subscribe(0, 20), subscribe(5, 25)]
    assert second.subscriptions == [subscribe(20, 40), subscribe(25, 45)]


@pytest.mark.parametrize(
    "kind", ["catch", "catch_iterable", "resume", "resume_operator"]
)
def test_disposed_recovery_does_not_advance_next_subscription(kind: str) -> None:
    scheduler = TestScheduler()
    first = scheduler.create_cold_observable(
        on_next(10, 1), on_error(20, ValueError("first"))
    )
    second = scheduler.create_cold_observable(on_next(10, 2), on_completed(20))
    source = recover(kind, first, second)
    one = scheduler.create_observer()
    two = scheduler.create_observer()
    disposable = source.subscribe(one, scheduler=scheduler)
    scheduler.advance_to(5)
    disposable.dispose()
    source.subscribe(two, scheduler=scheduler)
    scheduler.advance_to(100)
    assert one.messages == []
    assert two.messages == [on_next(15, 1), on_next(35, 2), on_completed(45)]
    assert first.subscriptions == [subscribe(0, 5), subscribe(5, 25)]
    assert second.subscriptions == [subscribe(25, 45)]


def test_resume_factory_receives_each_subscriptions_exception() -> None:
    error = ValueError("first")
    errors: list[Exception | None] = []
    values: list[int] = []

    def factory(cause: Exception | None) -> Observable[int]:
        errors.append(cause)
        return reactivex.just(2)

    source = reactivex.on_error_resume_next(reactivex.throw(error), factory)
    source.subscribe(values.append)
    source.subscribe(values.append)
    assert values == [2, 2]
    assert errors == [error, error]


def test_catch_generator_stays_single_pass() -> None:
    sources = (reactivex.just(value) for value in [1, 2])
    source = reactivex.catch_with_iterable(sources)
    values: list[int] = []
    source.subscribe(values.append)
    source.subscribe(values.append)
    source.subscribe(values.append)
    assert values == [1, 2]
