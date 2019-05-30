"""
This example shows how you can retry subscriptions that might
sometime fail with an error.

Note: you cannot use ref_count() in this case since that would
make publish() re-subscribe the cold-observable and it would start
looping forever.
"""

import time

import rx
from rx import operators as ops


def failing(x):
    x = int(x)
    if not x % 2:
        raise Exception("Error")
    return x


def main():
    xs = rx.from_marbles("1-2-3-4-5-6-7-9-|").pipe(ops.publish())
    xs.pipe(
        ops.map(failing),
        ops.retry()
    ).subscribe(print)

    xs.connect()  # Must connect. Cannot use ref_count() with publish()

    time.sleep(5)


if __name__ == '__main__':
    main()
