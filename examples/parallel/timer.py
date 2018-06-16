import concurrent.futures
import time
import rx

seconds = [5, 1, 2, 4, 3]


def sleep(tm):
    time.sleep(tm)
    return tm


def output(result):
    print('%d seconds' % result)

with concurrent.futures.ProcessPoolExecutor(5) as executor:
    rx.Observable.from_(seconds).flat_map(
        lambda s: executor.submit(sleep, s)
    ).subscribe_(output)

# 1 seconds
# 2 seconds
# 3 seconds
# 4 seconds
# 5 seconds
