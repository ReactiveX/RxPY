import unittest
from typing import Any, Callable, NoReturn

from reactivex import abc, create, empty, return_value, throw
from reactivex import operators as ops
from reactivex.disposable import SerialDisposable
from reactivex.internal.basic import noop
from reactivex.observable.observable import Observable
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


# Helper function for raising exceptions within lambdas


def _raise(ex: Any) -> NoReturn:
    raise RxException(ex)


class TestSelect(unittest.TestCase):
    def test_starmap_never(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable()

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == []
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 1000)]
        assert invoked[0] == 0

    def test_starmap_empty(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            # 200 subscribe
            on_completed(300),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [on_completed(300)]
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 300)]
        assert invoked[0] == 0

    def test_starmap_subscription_error(self) -> None:
        mapper: Callable[[Observable[tuple[int, int]]], Observable[tuple[int, int]]] = ops.starmap(lambda x, y: tuple[int, int]((x, y)))

        with self.assertRaises(RxException):
            return_value((1, 10)).pipe(mapper).subscribe(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            throw("ex").pipe(mapper).subscribe(on_error=lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            empty().pipe(mapper).subscribe(
                noop, noop, lambda: _raise("ex")
            )

        def subscribe(
            observer: abc.ObserverBase[Any], scheduler: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            _raise("ex")

        with self.assertRaises(RxException):
            create(subscribe).pipe(mapper).subscribe()

    def test_starmap_dispose_inside_mapper(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(110, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(310, (3, 30)),
            on_next(410, (4, 40)),
        )

        results: Any = scheduler.create_observer()
        d: SerialDisposable = SerialDisposable()
        invoked: list[int] = [0]

        def mapper(x: int, y: int) -> int:
            invoked[0] += 1
            if scheduler.clock > 250:
                d.dispose()
            return x + y

        d.disposable = xs.pipe(ops.starmap(mapper)).subscribe(results, scheduler=scheduler)

        def action(
            scheduler: abc.SchedulerBase, state: Any
        ) -> abc.DisposableBase | None:
            return d.dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action)
        scheduler.start()

        assert results.messages == [on_next(110, 11), on_next(210, 22)]

        assert xs.subscriptions == [ReactiveTest.subscribe(0, 310)]
        assert invoked[0] == 3

    def test_starmap_completed(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, "ex"),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_not_completed(self) -> None:
        scheduler = TestScheduler()
        invoked: list[int] = [0]
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
        )

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
        ]

        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_starmap_no_mapper(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, "ex"),
        )

        def factory() -> Observable[tuple[int, int]]:
            return xs.pipe(ops.starmap())

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]

    def test_starmap_mapper_with_one_element(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1,)),
            # 200 subscribe
            on_next(210, (2,)),
            on_next(240, (3,)),
            on_next(290, (4,)),
            on_next(350, (5,)),
            on_completed(400),
            on_next(410, (-1,)),
            on_completed(420),
            on_error(430, "ex"),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int) -> int:
                invoked[0] += 1
                return x * 10

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 20),
            on_next(240, 30),
            on_next(290, 40),
            on_next(350, 50),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_with_three_elements(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10, 100)),
            # 200 subscribe
            on_next(210, (2, 20, 200)),
            on_next(240, (3, 30, 300)),
            on_next(290, (4, 40, 400)),
            on_next(350, (5, 50, 500)),
            on_completed(400),
            on_next(410, (-1, -10, -100)),
            on_completed(420),
            on_error(430, "ex"),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int, y: int, z: int) -> int:
                invoked[0] += 1
                return x + y + z

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 222),
            on_next(240, 333),
            on_next(290, 444),
            on_next(350, 555),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_with_args(self) -> None:
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, "ex"),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(*args: int) -> int:
                invoked[0] += 1
                return sum(args)

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_error(self) -> None:
        scheduler = TestScheduler()
        ex: str = "ex"
        invoked: list[int] = [0]
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_error(400, ex),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, ex),
        )

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_error(400, ex),
        ]

        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_error(self) -> None:
        scheduler = TestScheduler()
        invoked: list[int] = [0]
        ex: str = "ex"
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, ex),
        )

        def factory() -> Observable[int]:
            def mapper(x: int, y: int) -> int:
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return x + y

            return xs.pipe(ops.starmap(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_error(290, ex),
        ]

        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3


class TestStarmapIndexed(unittest.TestCase):
    def test_starmap_indexed_throws(self) -> None:
        """Test starmap_indexed with subscription errors."""
        mapper: Callable[[Observable[tuple[int, int, int]]], Observable[int]] = ops.starmap_indexed(lambda x, y, index: x)

        with self.assertRaises(RxException):
            return_value((1, 10, 0)).pipe(mapper).subscribe(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            throw("ex").pipe(mapper).subscribe(on_error=lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            empty().pipe(mapper).subscribe(
                noop, noop, lambda: _raise("ex")
            )

        def subscribe(
            observer: abc.ObserverBase[Any], scheduler: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            _raise("ex")

        with self.assertRaises(RxException):
            create(subscribe).pipe(mapper).subscribe()

    def test_starmap_indexed_dispose_inside_mapper(self) -> None:
        """Test disposal within starmap_indexed mapper function."""
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            on_next(100, (4, 40, 0)),
            on_next(200, (3, 30, 1)),
            on_next(500, (2, 20, 2)),
            on_next(600, (1, 10, 3)),
        )
        invoked: list[int] = [0]
        results: Any = scheduler.create_observer()
        d: SerialDisposable = SerialDisposable()

        def projection(x: int, y: int, index: int) -> int:
            invoked[0] += 1
            if scheduler.clock > 400:
                d.dispose()
            return x + y + index * 100

        d.disposable = xs.pipe(ops.starmap_indexed(projection)).subscribe(
            results, scheduler=scheduler
        )

        def action(
            scheduler: abc.SchedulerBase, state: Any
        ) -> abc.DisposableBase | None:
            return d.dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action)
        scheduler.start()
        assert results.messages == [on_next(100, 44), on_next(200, 133)]
        assert xs.subscriptions == [ReactiveTest.subscribe(0, 500)]
        assert invoked[0] == 3

    def test_starmap_indexed_completed(self) -> None:
        """Test starmap_indexed with completed observable."""
        scheduler = TestScheduler()
        invoked: list[int] = [0]
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            on_next(180, (5, 50, 0)),
            on_next(210, (4, 40, 0)),
            on_next(240, (3, 30, 1)),
            on_next(290, (2, 20, 2)),
            on_next(350, (1, 10, 3)),
            on_completed(400),
            on_next(410, (-1, -10, 4)),
            on_completed(420),
            on_error(430, "ex"),
        )

        def factory() -> Observable[int]:
            def projection(x: int, y: int, index: int) -> int:
                invoked[0] += 1
                return (x + 1) + (y + 10) + (index * 100)

            return xs.pipe(ops.starmap_indexed(projection))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 55),
            on_next(240, 144),
            on_next(290, 233),
            on_next(350, 322),
            on_completed(400),
        ]
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_indexed_not_completed(self) -> None:
        """Test starmap_indexed with observable that doesn't complete."""
        scheduler = TestScheduler()
        invoked: list[int] = [0]
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            on_next(180, (5, 50, 0)),
            on_next(210, (4, 40, 0)),
            on_next(240, (3, 30, 1)),
            on_next(290, (2, 20, 2)),
            on_next(350, (1, 10, 3)),
        )

        def factory() -> Observable[int]:
            def projection(x: int, y: int, index: int) -> int:
                invoked[0] += 1
                return (x + 1) + (y + 10) + (index * 100)

            return xs.pipe(ops.starmap_indexed(projection))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 55),
            on_next(240, 144),
            on_next(290, 233),
            on_next(350, 322),
        ]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_starmap_indexed_error(self) -> None:
        """Test starmap_indexed with observable that errors."""
        scheduler = TestScheduler()
        ex: str = "ex"
        invoked: list[int] = [0]
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            on_next(180, (5, 50, 0)),
            on_next(210, (4, 40, 0)),
            on_next(240, (3, 30, 1)),
            on_next(290, (2, 20, 2)),
            on_next(350, (1, 10, 3)),
            on_error(400, ex),
            on_next(410, (-1, -10, 4)),
            on_completed(420),
            on_error(430, "ex"),
        )

        def factory() -> Observable[int]:
            def projection(x: int, y: int, index: int) -> int:
                invoked[0] += 1
                return (x + 1) + (y + 10) + (index * 100)

            return xs.pipe(ops.starmap_indexed(projection))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 55),
            on_next(240, 144),
            on_next(290, 233),
            on_next(350, 322),
            on_error(400, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_indexed_mapper_throws(self) -> None:
        """Test starmap_indexed with mapper that throws exception."""
        scheduler = TestScheduler()
        invoked: list[int] = [0]
        ex: str = "ex"
        xs: Observable[tuple[int, int, int]] = scheduler.create_hot_observable(
            on_next(180, (5, 50, 0)),
            on_next(210, (4, 40, 0)),
            on_next(240, (3, 30, 1)),
            on_next(290, (2, 20, 2)),
            on_next(350, (1, 10, 3)),
            on_completed(400),
            on_next(410, (-1, -10, 4)),
            on_completed(420),
            on_error(430, "ex"),
        )

        def factory() -> Observable[int]:
            def projection(x: int, y: int, index: int) -> int:
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)
                return (x + 1) + (y + 10) + (index * 100)

            return xs.pipe(ops.starmap_indexed(projection))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 55),
            on_next(240, 144),
            on_error(290, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3

    def test_starmap_indexed_with_three_elements(self) -> None:
        """Test starmap_indexed with three element tuples plus index."""
        scheduler = TestScheduler()
        xs: Observable[tuple[int, int, int, int]] = scheduler.create_hot_observable(
            on_next(180, (1, 10, 100, 0)),
            on_next(210, (2, 20, 200, 0)),
            on_next(240, (3, 30, 300, 1)),
            on_next(290, (4, 40, 400, 2)),
            on_next(350, (5, 50, 500, 3)),
            on_completed(400),
            on_next(410, (-1, -10, -100, 4)),
            on_completed(420),
            on_error(430, "ex"),
        )

        invoked: list[int] = [0]

        def factory() -> Observable[int]:
            def mapper(x: int, y: int, z: int, index: int) -> int:
                invoked[0] += 1
                return x + y + z + (index * 1000)

            return xs.pipe(ops.starmap_indexed(mapper))

        results: Any = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 222),
            on_next(240, 1333),
            on_next(290, 2444),
            on_next(350, 3555),
            on_completed(400),
        ]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_indexed_verifies_index_usage(self) -> None:
        """Test that starmap_indexed actually uses the index parameter."""
        scheduler = TestScheduler()
        # Create observable with tuples (value, index)
        xs: Observable[tuple[int, int]] = scheduler.create_hot_observable(
            on_next(210, (10, 0)),
            on_next(220, (10, 1)),
            on_next(230, (10, 2)),
            on_completed(250),
        )

        def factory() -> Observable[int]:
            # Multiply value by index - this will only work if index is passed
            return xs.pipe(ops.starmap_indexed(lambda value, index: value * index))

        results: Any = scheduler.start(factory)
        # If index is not passed, all results would be 0 (or error)
        # With index: 10*0=0, 10*1=10, 10*2=20
        assert results.messages == [
            on_next(210, 0),
            on_next(220, 10),
            on_next(230, 20),
            on_completed(250),
        ]


if __name__ == "__main__":
    unittest.main()
