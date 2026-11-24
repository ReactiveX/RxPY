from collections.abc import Iterator

from reactivex import operators as ops
from reactivex.subject import Subject


def test_zip_iterable_next_error_uses_error_channel_and_disposes_source():
    error = ValueError("invalid record")

    def records() -> Iterator[int]:
        yield 10
        raise error

    source: Subject[int] = Subject()
    values: list[tuple[int, int]] = []
    errors: list[Exception] = []
    completed: list[bool] = []
    source.pipe(ops.zip_with_iterable(records())).subscribe(
        values.append, errors.append, lambda: completed.append(True)
    )
    source.on_next(1)
    source.on_next(2)
    source.on_next(3)

    assert values == [(1, 10)]
    assert errors == [error]
    assert completed == []
    assert source.observers == []


def test_zip_iterable_iteration_error_can_be_recovered_with_catch():
    error = ValueError("invalid record")

    def records() -> Iterator[int]:
        raise error
        yield 10

    source: Subject[int] = Subject()
    fallback: Subject[tuple[int, int]] = Subject()
    values: list[tuple[int, int]] = []
    source.pipe(ops.zip_with_iterable(records()), ops.catch(fallback)).subscribe(
        values.append
    )
    source.on_next(1)
    fallback.on_next((2, 20))

    assert values == [(2, 20)]
    assert source.observers == []
