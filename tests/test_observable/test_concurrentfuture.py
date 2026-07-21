import asyncio
import unittest
from concurrent.futures import Future, ThreadPoolExecutor

import reactivex
from reactivex import operators as ops
from reactivex.internal import is_future


class TestIsFuture(unittest.TestCase):
    def test_is_future_concurrent(self) -> None:
        future: Future[int] = Future()
        assert is_future(future)

    def test_is_future_asyncio(self) -> None:
        loop = asyncio.new_event_loop()
        try:
            assert is_future(loop.create_future())
        finally:
            loop.close()

    def test_is_future_observable(self) -> None:
        assert not is_future(reactivex.of(1, 2, 3))

    def test_is_future_iterable(self) -> None:
        assert not is_future([1, 2, 3])


class TestFromConcurrentFuture(unittest.TestCase):
    def test_future_success(self) -> None:
        values: list[int] = []
        errors: list[Exception] = []
        completed: list[bool] = []

        future: Future[int] = Future()
        future.set_result(42)

        reactivex.from_future(future).subscribe(
            values.append, errors.append, lambda: completed.append(True)
        )

        assert values == [42]
        assert errors == []
        assert completed == [True]

    def test_future_failure(self) -> None:
        error = Exception("woops")
        values: list[int] = []
        errors: list[Exception] = []
        completed: list[bool] = []

        future: Future[int] = Future()
        future.set_exception(error)

        reactivex.from_future(future).subscribe(
            values.append, errors.append, lambda: completed.append(True)
        )

        assert values == []
        assert errors == [error]
        assert completed == []


class TestConcurrentFutureOperators(unittest.TestCase):
    """Concurrent futures should be lifted just like asyncio futures.

    See https://github.com/ReactiveX/RxPY/issues/709
    """

    def test_flat_map_concurrent_future(self) -> None:
        futures: dict[int, Future[int]] = {x: Future() for x in (1, 2, 3)}
        values: list[int] = []
        completed: list[bool] = []

        reactivex.from_(list(futures)).pipe(
            ops.flat_map(lambda x: futures[x])
        ).subscribe(values.append, on_completed=lambda: completed.append(True))

        assert values == []

        for x, future in futures.items():
            future.set_result(x * 10)

        assert values == [10, 20, 30]
        assert completed == [True]

    def test_flat_map_executor(self) -> None:
        values: list[int] = []

        # Leaving the context manager shuts the executor down, which waits
        # for all the submitted futures to complete.
        with ThreadPoolExecutor(3) as executor:
            reactivex.from_([1, 2, 3]).pipe(
                ops.flat_map(lambda x: executor.submit(lambda: x * 10))
            ).subscribe(values.append)

        assert sorted(values) == [10, 20, 30]

    def test_merge_all_concurrent_future(self) -> None:
        future: Future[int] = Future()
        values: list[int] = []

        reactivex.of(future).pipe(ops.merge_all()).subscribe(values.append)
        future.set_result(42)

        assert values == [42]

    def test_switch_latest_concurrent_future(self) -> None:
        future: Future[int] = Future()
        values: list[int] = []

        reactivex.of(future).pipe(ops.switch_latest()).subscribe(values.append)
        future.set_result(42)

        assert values == [42]

    def test_take_until_concurrent_future(self) -> None:
        future: Future[int] = Future()
        subject: reactivex.Subject[int] = reactivex.Subject()
        values: list[int] = []
        completed: list[bool] = []

        subject.pipe(ops.take_until(future)).subscribe(
            values.append, on_completed=lambda: completed.append(True)
        )

        subject.on_next(1)
        future.set_result(0)
        subject.on_next(2)

        assert values == [1]
        assert completed == [True]

    def test_amb_concurrent_future(self) -> None:
        future: Future[int] = Future()
        subject: reactivex.Subject[int] = reactivex.Subject()
        values: list[int] = []

        subject.pipe(ops.amb(future)).subscribe(values.append)

        future.set_result(42)
        subject.on_next(1)

        assert values == [42]

    def test_defer_concurrent_future(self) -> None:
        future: Future[int] = Future()
        future.set_result(42)
        values: list[int] = []

        reactivex.defer(lambda _: future).subscribe(values.append)

        assert values == [42]

    def test_if_then_concurrent_future(self) -> None:
        future: Future[int] = Future()
        future.set_result(42)
        values: list[int] = []

        reactivex.if_then(lambda: True, future).subscribe(values.append)

        assert values == [42]

    def test_case_concurrent_future(self) -> None:
        future: Future[int] = Future()
        future.set_result(42)
        values: list[int] = []

        sources: dict[str, reactivex.Observable[int]] = {}
        reactivex.case(lambda: "missing", sources, future).subscribe(values.append)

        assert values == [42]

    def test_start_async_concurrent_future(self) -> None:
        future: Future[int] = Future()
        future.set_result(42)
        values: list[int] = []

        reactivex.start_async(lambda: future).subscribe(values.append)

        assert values == [42]

    def test_on_error_resume_next_concurrent_future(self) -> None:
        future: Future[int] = Future()
        future.set_result(42)
        values: list[int] = []

        reactivex.on_error_resume_next(
            reactivex.throw(Exception("x")), future
        ).subscribe(values.append)

        assert values == [42]
