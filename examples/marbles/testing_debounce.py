from reactivex import operators as ops
from reactivex.testing.marbles import marbles_testing

"""
Tests debounceTime from reactivexjs
https://github.com/ReactiveX/rxjs/blob/master/spec/operators/debounceTime-spec.ts

it should delay all element by the specified time
"""
with marbles_testing(timespan=1.0) as (start, cold, hot, exp):
    e1 = cold("-a--------b------c----|")
    ex = exp("------a--------b------(c,|)")
    expected = ex

    def create():
        return e1.pipe(
            ops.debounce(5),
        )

    results = start(create)
    assert results == expected

print("debounce: results vs expected")
for r, e in zip(results, expected):
    print(r, e)
