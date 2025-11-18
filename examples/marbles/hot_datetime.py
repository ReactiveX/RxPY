import datetime

import reactivex
import reactivex.operators as ops

"""
Delay the emission of elements to the specified datetime.
"""

now = datetime.datetime.now(datetime.timezone.utc)
dt = datetime.timedelta(seconds=3.0)
duetime = now + dt

print(f"{now} ->  now\n" f"{duetime} ->  start of emission in {dt.total_seconds()}s")

hot = reactivex.hot("10--11--12--13--(14,|)", timespan=0.2, duetime=duetime)

source = hot.pipe(ops.do_action(print))
source.run()
