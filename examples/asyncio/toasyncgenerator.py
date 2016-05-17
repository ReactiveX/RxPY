import rx
asyncio = rx.config['asyncio']

from rx.concurrency import AsyncIOScheduler
from rx.core import Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def to_async_generator(self, future_ctor=None, sentinel=None):
    future_ctor = future_ctor or rx.config.get("Future")
    if not future_ctor:
        raise Exception('Future type not provided nor in rx.config.Future')

    loop = asyncio.get_event_loop()
    future = [future_ctor()]
    notifications = []

    def feeder():
        if not len(notifications) or future[0].done():
            return

        notification = notifications.pop(0)

        if notification.kind == "E":
            future[0].set_exception(notification.exception)
        elif notification.kind == "C":
            future[0].set_exception(StopIteration(sentinel))
        else:
            future[0].set_result(notification.value)

    def on_next(value):
        """Takes on_next values and appends them to the notification queue"""

        notifications.append(value)
        loop.call_soon(feeder)

    self.materialize().subscribe(on_next)

    @asyncio.coroutine
    def gen():
        """Generator producing futures"""

        loop.call_soon(feeder)
        future[0] = future_ctor()

        return future[0]
    return gen


@asyncio.coroutine
def go():
    scheduler = AsyncIOScheduler()

    xs = Observable.from_([x for x in range(10)], scheduler=scheduler)
    gen = xs.to_async_generator()

    # Wish we could write something like:
    # ys = (x for x in yield from gen())
    while True:
        x = yield from gen()
        if x is None:
            break
        print(x)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go())

if __name__ == '__main__':
    main()
