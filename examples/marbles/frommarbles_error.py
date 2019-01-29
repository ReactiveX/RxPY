import time

import rx
from rx import concurrency as ccy
from rx.testing import marbles

err = ValueError("I don't like 5!")

src0 = marbles.from_marbles('12-----4-----67--|', timespan=0.2)
src1 = marbles.from_marbles('----3----5-#      ', timespan=0.2, error=err)

source = rx.merge(src0, src1)
source.subscribe(
    on_next=print,
    on_error=lambda e: print('boom!! {}'.format(e)),
    on_completed=lambda: print('good job!'),
    scheduler=ccy.timeout_scheduler,
    )

time.sleep(3)
