import unittest

import reactivex
from reactivex import operators as ops


class TestGroupByReduce(unittest.TestCase):
    def test_groupby_count(self):
        res = []
        counts = reactivex.from_(range(10)).pipe(
            ops.group_by(lambda i: "even" if i % 2 == 0 else "odd"),
            ops.flat_map(
                lambda i: i.pipe(
                    ops.count(),
                    ops.map(lambda ii: (i.key, ii)),
                )
            ),
        )

        counts.subscribe(on_next=res.append)
        assert res == [("even", 5), ("odd", 5)]

    def test_window_sum(self):
        res = []
        reactivex.from_(range(6)).pipe(
            ops.window_with_count(count=3, skip=1),
            ops.flat_map(
                lambda i: i.pipe(
                    ops.sum(),
                )
            ),
        ).subscribe(on_next=res.append)

        assert res == [3, 6, 9, 12, 9, 5, 0]
