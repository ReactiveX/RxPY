import pytest

import reactivex
from reactivex import Observable, abc
from reactivex.scheduler import ImmediateScheduler
from reactivex.testing import ReactiveTest, TestScheduler


class CountingResource(abc.DisposableBase):
    def __init__(self) -> None:
        self.disposals = 0

    def dispose(self) -> None:
        self.disposals += 1


@pytest.mark.parametrize(
    "stage", ["factory", "subscribe", "error", "next", "completed"]
)
def test_using_disposes_resource_when_subscription_raises(stage: str) -> None:
    resource = CountingResource()
    error = RuntimeError("subscription failed")

    def fail(*args: object) -> None:
        raise error

    def factory(value: abc.DisposableBase | None) -> Observable[int]:
        assert value is resource
        if stage == "factory":
            raise error
        if stage == "subscribe":
            return reactivex.create(fail)
        if stage == "error":
            return reactivex.throw(error)
        if stage == "next":
            return reactivex.just(1, scheduler=ImmediateScheduler())
        return reactivex.empty()

    with pytest.raises(RuntimeError) as raised:
        reactivex.using(lambda: resource, factory).subscribe(
            on_next=fail if stage == "next" else None,
            on_completed=fail if stage == "completed" else None,
        )

    assert raised.value is error
    assert resource.disposals == 1


@pytest.mark.parametrize("factory_raises", [False, True])
def test_using_disposes_resource_when_error_handler_raises(
    factory_raises: bool,
) -> None:
    resource = CountingResource()
    source_error = ValueError("source failed")
    observer_error = RuntimeError("observer failed")
    errors = []

    def factory(value: abc.DisposableBase | None) -> Observable[int]:
        if factory_raises:
            raise source_error
        return reactivex.throw(source_error)

    def on_error(error: Exception) -> None:
        errors.append(error)
        raise observer_error

    with pytest.raises(RuntimeError) as raised:
        reactivex.using(lambda: resource, factory).subscribe(on_error=on_error)

    assert raised.value is observer_error
    assert errors == [source_error]
    assert resource.disposals == 1


@pytest.mark.parametrize("factory_raises", [False, True])
def test_using_handled_error_disposes_resource_once(factory_raises: bool) -> None:
    resource = CountingResource()
    error = RuntimeError("source failed")
    errors = []

    def factory(value: abc.DisposableBase | None) -> Observable[int]:
        if factory_raises:
            raise error
        return reactivex.throw(error)

    subscription = reactivex.using(lambda: resource, factory).subscribe(
        on_error=errors.append
    )
    subscription.dispose()
    assert errors == [error]
    assert resource.disposals == 1


def test_using_scheduled_error_preserves_lifetime() -> None:
    resource = CountingResource()
    scheduler = TestScheduler()
    error = RuntimeError("source failed")
    source = scheduler.create_cold_observable(ReactiveTest.on_error(10, error))
    results = scheduler.start(
        lambda: reactivex.using(lambda: resource, lambda _: source)
    )
    assert results.messages == [ReactiveTest.on_error(210, error)]
    assert source.subscriptions == [ReactiveTest.subscribe(200, 210)]
    assert resource.disposals == 1


def test_using_null_resource_propagates_subscription_error() -> None:
    error = RuntimeError("source failed")
    with pytest.raises(RuntimeError) as raised:
        reactivex.using(lambda: None, lambda _: reactivex.throw(error)).subscribe()
    assert raised.value is error
