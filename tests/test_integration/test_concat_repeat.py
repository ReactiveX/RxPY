import unittest

from reactivex import operators as ops
from reactivex.testing.marbles import marbles_testing


class TestConcatIntegration(unittest.TestCase):
    def test_concat_repeat(self) -> None:
        with marbles_testing() as (start, cold, _hot, exp):
            e1 = cold("-e11-e12|", None, None)
            e2 = cold("-e21-e22|", None, None)
            ex = exp("-e11-e12-e21-e22-e11-e12-e21-e22|", None, None)

            obs = e1.pipe(ops.concat(e2), ops.repeat(2))

            results = start(obs)
            assert results == ex
