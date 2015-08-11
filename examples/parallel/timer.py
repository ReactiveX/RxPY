from __future__ import print_function

import rx
import concurrent.futures
import time

seconds = [5, 1, 2, 4, 3]


def sleep(t):
    time.sleep(t)
    return t


def output(result):
    print('%d seconds' % result)

with concurrent.futures.ProcessPoolExecutor(5) as executor:
    rx.Observable.from_(seconds).flat_map(
        lambda s: executor.submit(sleep, s)
    ).subscribe(output)

# 1 seconds
# 2 seconds
# 3 seconds
# 4 seconds
# 5 seconds
