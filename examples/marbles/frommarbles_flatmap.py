import time

import rx
from rx import operators as ops
from rx import concurrency as ccy

a = rx.cold(' ---a---a----------------a-|')
b = rx.cold('    ---b---b---|            ')
c = rx.cold('             ---c---c---|   ')
d = rx.cold('                --d---d---| ')
e1 = rx.cold('a--b--------c--d-------|   ')

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

time.sleep(3)
