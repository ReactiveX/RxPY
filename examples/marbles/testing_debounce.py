from rx import operators as ops
from rx.testing import marbles

"""
Tests debounceTime from rxjs
https://github.com/ReactiveX/rxjs/blob/master/spec/operators/debounceTime-spec.ts

it should delay all element by the specified time
"""

start, cold, hot, exp = marbles.test_context(timespan=1)

e1 = hot('-a--------b------c----|')
ex = exp('------a--------b------(c|)')
expected = ex


def create():
    return e1.pipe(
        ops.debounce(5),
        )


results = start(create)
assert results == expected

print('\ndebounce: results vs expected')
for r, e in zip(results, expected):
    print(r, e)

