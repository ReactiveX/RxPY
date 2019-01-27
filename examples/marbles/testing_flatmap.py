from rx import operators as ops
from rx.testing import marbles

"""
Tests MergeMap from rxjs
https://github.com/ReactiveX/rxjs/blob/master/spec/operators/mergeMap-spec.ts

it should flat_map many regular interval inners
"""
start, cold, hot, exp = marbles.test_context(timespan=1)

a = cold(' ----a---a---a---(a|)                    ')
b = cold('     ----1---b---(b|)                    ')
c = cold('                 ----c---c---c---c---(c|)')
d = cold('                         ----(d|)        ')
e1 = hot('-a---b-----------c-------d-------|       ')
ex = exp('-----a---(a1)(ab)(ab)c---c---(cd)c---(c|)')
expected = ex

observableLookup = {"a": a, "b": b, "c": c, "d": d}


def create():
    return e1.pipe(
        ops.flat_map(lambda value: observableLookup[value])
        )


results = start(create)
assert results == expected


print('\nflat_map: results vs expected')
for r, e in zip(results, expected):
    print(r, e)
