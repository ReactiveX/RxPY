import rx
asyncio = rx.config['asyncio']

from rx.concurrency import AsyncIOScheduler
from rx.observable import Observable
from rx.internal import extensionmethod

future_ctor = rx.config.get("Future") or asyncio.Future

@extensionmethod(Observable)
async def __aiter__(self):
    loop = asyncio.get_event_loop()
    source = self

    class AIterator:
        def __init__(self):
            self.notifications = []
            self.future = future_ctor()

            source.materialize().subscribe(self.on_next)

        def feeder(self):
            if not self.notifications or self.future.done():
                return

            notification = self.notifications.pop(0)
            dispatch = {
                'N': lambda: self.future.set_result(notification.value),
                'E': lambda: self.future.set_exception(notification.exception),
                'C': lambda: self.future.set_exception(StopAsyncIteration)
            }

            dispatch[notification.kind]()

        def on_next(self, notification):
            self.notifications.append(notification)
            self.feeder()

        async def __anext__(self):
            self.feeder()

            value = await self.future
            self.future = future_ctor()
            return value

    return AIterator()


async def go():
    scheduler = AsyncIOScheduler()

    xs = Observable.range(0, 10, scheduler=scheduler)
    async for x in xs:
        print("got %s" % x)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go())

if __name__ == '__main__':
    main()
