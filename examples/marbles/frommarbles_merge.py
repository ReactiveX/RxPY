import time

import rx
from rx import concurrency as ccy

source0 = rx.cold('a-----d---1--------4-|', timespan=0.1)
source1 = rx.cold('--b-c-------2---3-|   ', timespan=0.1)

observable = rx.merge(source0, source1)

observable.subscribe(
    on_next=print,
    on_error=lambda e: print('boom!! {}'.format(e)),
    on_completed=lambda: print('good job!'),
    scheduler=ccy.timeout_scheduler,
    )

time.sleep(3)
