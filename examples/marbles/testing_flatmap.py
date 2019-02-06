from rx import operators as ops
from rx.testing.marbles import marbles_testing

"""
Tests MergeMap from rxjs
https://github.com/ReactiveX/rxjs/blob/master/spec/operators/mergeMap-spec.ts

it should flat_map many regular interval inners
"""
with marbles_testing(timespan=1.0) as context:
    start, cold, hot, exp = context

    a = cold(' ----a---a----a----(a,|)                     ')
    b = cold('     ----1----b----(b,|)                     ')
    c = cold('                 -------c---c---c----c---(c,|)')
    d = cold('                         -------(d,|)        ')
    e1 = hot('-a---b-----------c-------d------------|      ')
    ex = exp('-----a---(a,1)(a,b)(a,b)c---c---(c,d)c---(c,|)')
    expected = ex

    observableLookup = {"a": a, "b": b, "c": c, "d": d}

    obs = e1.pipe(
        ops.flat_map(lambda value: observableLookup[value])
        )

    results = start(obs)
    assert results == expected

print('flat_map: results vs expected')
for r, e in zip(results, expected):
    print(r, e)
