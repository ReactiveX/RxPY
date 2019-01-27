import rx
from rx import concurrency as ccy
from rx.testing import marbles

lookup0 = {'a': 1, 'b': 3, 'c': 5}
lookup1 = {'x': 2, 'y': 4, 'z': 6}
source0 = marbles.from_marbles('a---b----c----|', timespan=0.2, lookup=lookup0)
source1 = marbles.from_marbles('---x---y---z--|', timespan=0.2, lookup=lookup1)

observable = rx.merge(source0, source1)

observable.subscribe_(
    on_next=print,
    on_error=lambda e: print('boom!! {}'.format(e)),
    on_completed=lambda: print('good job!'),
    scheduler=ccy.timeout_scheduler,
    )

