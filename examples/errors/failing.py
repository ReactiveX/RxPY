"""
This example shows how you can retry subscriptions that might
sometime fail with an error.

Note: you cannot use ref_count() in this case since that would
make publish() re-subscribe the cold-observable and it would start
looping forever.
"""

import rx
from rx.testing import stringify  # noqa


def failing(x):
    x = int(x)
    if not x % 2:
        raise Exception("Error")
    return x


def main():
    xs = rx.Observable.from_string("1-2-3-4-5-6-7-9-|").publish()
    xs.map(failing).retry().subscribe(print)

    xs.connect()  # Must connect. Cannot use ref_count() with publish()

if __name__ == '__main__':
    main()
