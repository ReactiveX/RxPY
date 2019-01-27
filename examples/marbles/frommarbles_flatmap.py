from rx import operators as ops
from rx import concurrency as ccy
from rx.testing.marbles import from_marbles

a = from_marbles(' ---a---a----------------a-|')
b = from_marbles('    ---b---b---|            ')
c = from_marbles('             ---c---c---|   ')
d = from_marbles('                --d---d---| ')
e1 = from_marbles('a--b--------c--d-------|   ')

observableLookup = {"a": a, "b": b, "c": c, "d": d}

source = e1.pipe(
    ops.flat_map(lambda value: observableLookup[value]),
    )

source.subscribe_(
    on_next=print,
    on_error=lambda e: print('boom!! {}'.format(e)),
    on_completed=lambda: print('good job!'),
    scheduler=ccy.timeout_scheduler,
    )
