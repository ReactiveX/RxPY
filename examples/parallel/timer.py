import concurrent.futures
import time

import reactivex
from reactivex import operators as ops

seconds = [5, 1, 2, 4, 3]


def sleep(tm: float) -> float:
    time.sleep(tm)
    return tm


def output(result: float) -> None:
    print("%d seconds" % result)


# The __main__ guard is required by ProcessPoolExecutor for any start method
# that does not fork, e.g. "spawn" (Windows, macOS) and "forkserver".
if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor(5) as executor:
        reactivex.from_(seconds).pipe(
            ops.flat_map(lambda s: executor.submit(sleep, s))
        ).subscribe(output)

# 1 seconds
# 2 seconds
# 3 seconds
# 4 seconds
# 5 seconds
