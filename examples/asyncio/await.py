import asyncio
from rx import Observable


stream = Observable.just("Hello, world!")

async def hello_world():
    n = await stream
    print(n)

loop = asyncio.get_event_loop()
# Blocking call which returns when the hello_world() coroutine is done
loop.run_until_complete(hello_world())
loop.close()
