import concurrent.futures
import time

import reactivex
from reactivex import operators as ops

seconds = [5, 1, 2, 4, 3]


def sleep(tm: float) -> float:
    time.sleep(tm)
    return tm


def output(result: str) -> None:
    print("%d seconds" % result)


with concurrent.futures.ProcessPoolExecutor(5) as executor:
    reactivex.from_(seconds).pipe(
        ops.flat_map(lambda s: executor.submit(sleep, s))
    ).subscribe(output)

# 1 seconds
# 2 seconds
# 3 seconds
# 4 seconds
# 5 seconds
