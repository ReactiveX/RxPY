import rx
from rx import concurrency as ccy
from rx.testing import marbles

source0 = marbles.from_marbles('a-----d---1--------4-|', timespan=0.2)
source1 = marbles.from_marbles('--b-c-------2---3-|   ', timespan=0.2)

observable = rx.merge(source0, source1)

observable.subscribe(
    on_next=print,
    on_error=lambda e: print('boom!! {}'.format(e)),
    on_completed=lambda: print('good job!'),
    scheduler=ccy.timeout_scheduler,
    )
