import asyncio
from asyncio import Future

import rx
from rx import operators as ops
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.core import Observable


def to_async_generator(sentinel=None):
    loop = asyncio.get_event_loop()
    future = Future()
    notifications = []

    def _to_async_generator(source: Observable):

        def feeder():
            nonlocal future

            if not notifications or future.done():
                return

            notification = notifications.pop(0)

            if notification.kind == "E":
                future.set_exception(notification.exception)
            elif notification.kind == "C":
                future.set_result(sentinel)
            else:
                future.set_result(notification.value)

        def on_next(value):
            """Takes on_next values and appends them to the notification queue"""

            notifications.append(value)
            loop.call_soon(feeder)

        source.pipe(ops.materialize()).subscribe(on_next)

        async def gen():
            """Generator producing futures"""
            nonlocal future

            loop.call_soon(feeder)
            future = Future()

            return future
        return gen
    return _to_async_generator


async def go(loop):
    scheduler = AsyncIOScheduler(loop)

    xs = rx.from_([x for x in range(10)], scheduler=scheduler)
    gen = xs.pipe(to_async_generator())

    # Wish we could write something like:
    # ys = (x for x in yield from gen())
    while True:
        x = await gen()
        if x is None:
            break
        print(x)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go(loop))


if __name__ == '__main__':
    main()
