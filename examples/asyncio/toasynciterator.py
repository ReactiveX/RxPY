import rx
asyncio = rx.config['asyncio']
from collections.abc import AsyncIterable
from concurrent.futures import CancelledError

from rx.concurrency import AsyncIOScheduler
from rx.observable import Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
async def __aiter__(self):
    future_ctor = rx.config.get("Future")
    if not future_ctor:
        raise Exception('Future type not provided nor in rx.config.Future')

    loop = asyncio.get_event_loop()
    source = self

    class AIterator:
        def __init__(self):
            self.notifications = []
            self.running = True
            self.future = None

            source.materialize().subscribe(self.on_next)

        def feeder(self):
            # print("feeder")
            if not len(self.notifications):
                return

            if (not self.future) or self.future.done():
                return

            notification = self.notifications.pop(0)

            if notification.kind == "E":
                self.future.set_exception(notification.exception)
                self.running = False
            elif notification.kind == "C":
                self.future.cancel()
                self.running = False
            else:
                self.future.set_result(notification.value)

        def on_next(self, notification):
            self.notifications.append(notification)
            loop.call_soon(self.feeder)

        async def __anext__(self):
            """Returns awaitable"""
            loop.call_soon(self.feeder)

            if self.running:
                self.future = future_ctor()
            else:
                raise StopAsyncIteration

            return self.future

    return AIterator()


async def go():
    scheduler = AsyncIOScheduler()

    xs = Observable.range(0, 10, scheduler=scheduler)

    # Could wish for a comprehension expression
    async for x in xs:
        try:
            value = await x
        except CancelledError:
            print("OnComplete")
        else:
            print("got %s" % value)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go())

if __name__ == '__main__':
    main()
