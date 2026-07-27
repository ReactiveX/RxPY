import unittest
from collections.abc import Callable
from typing import Any

import reactivex
from reactivex import Observable
from reactivex import operators as ops


class TestGroupByReduce(unittest.TestCase):
    def test_groupby_count(self) -> None:
        res: list[Any] = []

        # Integration test: GroupedObservable types validated at runtime
        def flat_map_fn(i: Any) -> Any:
            return i.pipe(
                ops.count(),
                ops.map(lambda ii: (i.key, ii)),
            )

        flat_map_op: Callable[[Observable[Any]], Observable[Any]] = ops.flat_map(
            flat_map_fn
        )

        counts: Any = reactivex.from_(range(10)).pipe(
            ops.group_by(lambda i: "even" if i % 2 == 0 else "odd"),
            flat_map_op,
        )

        counts.subscribe(on_next=res.append)
        assert res == [("even", 5), ("odd", 5)]

    def test_window_sum(self) -> None:
        res: list[Any] = []

        # Integration test: windowed Observable types validated at runtime
        def flat_map_fn(i: Any) -> Any:
            return i.pipe(ops.sum())

        flat_map_op: Callable[[Observable[Any]], Observable[Any]] = ops.flat_map(
            flat_map_fn
        )

        obs: Any = reactivex.from_(range(6)).pipe(
            ops.window_with_count(count=3, skip=1),
            flat_map_op,
        )
        obs.subscribe(on_next=res.append)

        assert res == [3, 6, 9, 12, 9, 5, 0]
