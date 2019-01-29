# -*- coding: utf-8 -*-

from rx.testing import marbles
import rx.concurrency as ccy
import datetime

#start_time = 5
now =  datetime.datetime.utcnow()
start_time = now + datetime.timedelta(seconds=1.0)
hot = marbles.hot('--a--b--c--|',
#                   timespan=0.3,
                   start_time=start_time,
#                   scheduler=ccy.timeout_scheduler,
                   )

hot.subscribe(print, print, lambda: print('completed'))
