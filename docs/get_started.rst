.. get_started

Get Started
============

An :class:`Observable <reactivex.Observable>` is the core type in ReactiveX. It
serially pushes items, known as *emissions*, through a series of operators until
it finally arrives at an Observer, where they are
consumed.

Push-based (rather than pull-based) iteration opens up powerful new
possibilities to express code and concurrency much more quickly. Because an
:class:`Observable <reactivex.Observable>` treats events as data and data as events,
composing the two together becomes trivial.

There are many ways to create an :class:`Observable <reactivex.Observable>` that hands
items to an Observer. You can use a :func:`create()
<reactivex.create>` factory and pass it functions that handle items:

* The *on_next* function is called each time the Observable emits an item.
* The *on_completed* function is called when the Observable completes.
* The *on_error* function is called when an error occurs on the Observable.

You do not have to specify all three event types. You can pick and choose which
events you want to observe by providing only some of the callbacks, or simply by
providing a single lambda for *on_next*. Typically in production, you will want
to provide an *on_error* handler so that errors are explicitly handled by the
subscriber.

Let's consider the following example:

.. code:: python

    from reactivex import create

    def push_five_strings(observer, scheduler):
        observer.on_next("Alpha")
        observer.on_next("Beta")
        observer.on_next("Gamma")
        observer.on_next("Delta")
        observer.on_next("Epsilon")
        observer.on_completed()

    source = create(push_five_strings)

    source.subscribe(
        on_next = lambda i: print("Received {0}".format(i)),
        on_error = lambda e: print("Error Occurred: {0}".format(e)),
        on_completed = lambda: print("Done!"),
    )

An Observable is created with create. On subscription, the *push_five_strings*
function is called. This function emits five items. The three callbacks provided
to the *subscribe* function simply print the received items and completion
states. Note that the use of lambdas simplify the code in this basic example.

Output:

.. code:: console

    Received Alpha
    Received Beta
    Received Gamma
    Received Delta
    Received Epsilon
    Done!

However, there are many :ref:`Observable factories
<reference_observable_factory>` for common sources of emissions. To simply push
five items, we can rid the :func:`create() <reactivex.create>` and its backing
function, and use :func:`of() <reactivex.of>`. This factory accepts an argument list,
iterates on each argument to emit them as items, and the completes. Therefore,
we can simply pass these five Strings as arguments to it:

.. code:: python

    from reactivex import of

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe(
        on_next = lambda i: print("Received {0}".format(i)),
        on_error = lambda e: print("Error Occurred: {0}".format(e)),
        on_completed = lambda: print("Done!"),
    )

And a single parameter can be provided to the subscribe function if completion
and error are ignored:

.. code:: python

    from reactivex import of

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe(lambda value: print("Received {0}".format(value)))

Output:

.. code:: console

    Received Alpha
    Received Beta
    Received Gamma
    Received Delta
    Received Epsilon

Operators and Chaining
--------------------------

You can also derive new Observables using over 130 operators available in RxPY.
Each operator will yield a new :class:`Observable <reactivex.Observable>` that
transforms emissions from the source in some way. For example, we can
:func:`map() <reactivex.operators.map>` each `String` to its length, then
:func:`filter() <reactivex.operators.filter>` for lengths being at least 5. These will
yield two separate Observables built off each other.

.. code:: python

    from reactivex import of, operators as op

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    composed = source.pipe(
        op.map(lambda s: len(s)),
        op.filter(lambda i: i >= 5)
    )
    composed.subscribe(lambda value: print("Received {0}".format(value)))

Output:

.. code:: console

    Received 5
    Received 5
    Received 5
    Received 7

Typically, you do not want to save Observables into intermediary variables for
each operator, unless you want to have multiple subscribers at that point.
Instead, you want to strive to inline and create an "Observable pipeline" of
operations. That way your code is readable and tells a story much more easily.

.. code:: python

    from reactivex import of, operators as op

    of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        op.map(lambda s: len(s)),
        op.filter(lambda i: i >= 5)
    ).subscribe(lambda value: print("Received {0}".format(value)))

Custom operator
---------------

As operators chains grow up, the chains must be split to make the code more
readable. New operators are implemented as functions, and can be directly used
in the *pipe* operator. When an operator is implemented as a composition of
other operators, then the implementation is straightforward, thanks to the
*pipe* function:

.. code:: python

    import reactivex
    from reactivex import operators as ops

    def length_more_than_5():
        return rx.pipe(
            ops.map(lambda s: len(s)),
            ops.filter(lambda i: i >= 5),
        )

    reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        length_more_than_5()
    ).subscribe(lambda value: print("Received {0}".format(value)))

In this example, the *map* and *filter* operators are grouped in a new
*length_more_than_5* operator.

It is also possible to create an operator that is not a composition of other
operators. This allows to fully control the subscription logic and items
emissions:

 .. code:: python

    import reactivex

    def lowercase():
        def _lowercase(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):
                    observer.on_next(value.lower())

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return reactivex.create(subscribe)
        return _lowercase

    reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
            lowercase()
         ).subscribe(lambda value: print("Received {0}".format(value)))

In this example, the *lowercase* operator converts all received items to
lowercase. The structure of the *_lowercase* function is a very common way to
implement custom operators: It takes a source Observable as input, and returns a
custom Observable. The source observable is subscribed only when the output
Observable is subscribed. This allows to chain subscription calls when building
a pipeline.

Output:

.. code:: console

    Received alpha
    Received beta
    Received gamma
    Received delta
    Received epsilon

Concurrency
-----------

CPU Concurrency
................

To achieve concurrency, you use two operators: :func:`subscribe_on()
<reactivex.operators.subscribe_on>` and :func:`observe_on() <reactivex.operators.observe_on>`.
Both need a :ref:`Scheduler <reference_scheduler>` which provides a thread for
each subscription to do work (see section on Schedulers below). The
:class:`ThreadPoolScheduler <reactivex.scheduler.ThreadPoolScheduler>` is a good
choice to create a pool of reusable worker threads.

.. attention::

    `GIL <https://wiki.python.org/moin/GlobalInterpreterLock>`_ has the potential to
    undermine your concurrency performance, as it prevents multiple threads from
    accessing the same line of code simultaneously. Libraries like
    `NumPy <http://www.numpy.org/>`_ can mitigate this for parallel intensive
    computations as they free the GIL. RxPy may also minimize thread overlap to some
    degree. Just be sure to test your application with concurrency and ensure there
    is a performance gain.

The :func:`subscribe_on() <reactivex.operators.subscribe_on>` instructs the source
:class:`Observable <reactivex.Observable>` at the start of the chain which scheduler to
use (and it does not matter where you put this operator). The
:func:`observe_on() <reactivex.operators.observe_on>`, however, will switch to a
different *Scheduler* **at that point** in the *Observable* chain, effectively
moving an emission from one thread to another. Some :ref:`Observable factories
<reference_observable_factory>` and :ref:`operators
<reference_operators>`, like :func:`interval() <reactivex.interval>` and
:func:`delay() <reactivex.operators.delay>`, already have a default *Scheduler* and
thus will ignore any :func:`subscribe_on() <reactivex.operators.subscribe_on>` you
specify (although you can pass a *Scheduler* usually as an argument).

Below, we run three different processes concurrently rather than sequentially
using :func:`subscribe_on() <reactivex.operators.subscribe_on>` as well as an
:func:`observe_on() <reactivex.operators.observe_on>`.

.. code:: python

    import multiprocessing
    import random
    import time
    from threading import current_thread

    import reactivex
    from reactivex.scheduler import ThreadPoolScheduler
    from reactivex import operators as ops


    def intense_calculation(value):
        # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
        time.sleep(random.randint(5, 20) * 0.1)
        return value


    # calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    # Create Process 1
    reactivex.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
    ).subscribe(
        on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
        on_error=lambda e: print(e),
        on_completed=lambda: print("PROCESS 1 done!"),
    )

    # Create Process 2
    reactivex.range(1, 10).pipe(
        ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
    ).subscribe(
        on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
        on_error=lambda e: print(e),
        on_completed=lambda: print("PROCESS 2 done!"),
    )

    # Create Process 3, which is infinite
    reactivex.interval(1).pipe(
        ops.map(lambda i: i * 100),
        ops.observe_on(pool_scheduler),
        ops.map(lambda s: intense_calculation(s)),
    ).subscribe(
        on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
        on_error=lambda e: print(e),
    )

    input("Press Enter key to exit\n")

**OUTPUT:**

.. code:: console

    Press Enter key to exit
    PROCESS 1: Thread-1 Alpha
    PROCESS 2: Thread-2 1
    PROCESS 3: Thread-4 0
    PROCESS 2: Thread-2 2
    PROCESS 1: Thread-1 Beta
    PROCESS 3: Thread-7 100
    PROCESS 3: Thread-7 200
    PROCESS 2: Thread-2 3
    PROCESS 1: Thread-1 Gamma
    PROCESS 1: Thread-1 Delta
    PROCESS 2: Thread-2 4
    PROCESS 3: Thread-7 300


IO Concurrency
................

IO concurrency is also supported for several asynchronous frameworks, in
combination with associated RxPY schedulers. The following example implements
a simple echo TCP server that delays its answers by 5 seconds. It uses AsyncIO
as an event loop.

The TCP server is implemented in AsyncIO, and the echo logic is implemented as
an RxPY operator chain. Futures allow the operator chain to drive the loop of
the coroutine.

.. code:: python

    from collections import namedtuple
    import asyncio
    import reactivex
    import reactivex.operators as ops
    from reactivex.subject import Subject
    from reactivex.scheduler.eventloop import AsyncIOScheduler

    EchoItem = namedtuple('EchoItem', ['future', 'data'])


    def tcp_server(sink, loop):
        def on_subscribe(observer, scheduler):
            async def handle_echo(reader, writer):
                print("new client connected")
                while True:
                    data = await reader.readline()
                    data = data.decode("utf-8")
                    if not data:
                        break

                    future = asyncio.Future()
                    observer.on_next(EchoItem(
                        future=future,
                        data=data
                    ))
                    await future
                    writer.write(future.result().encode("utf-8"))

                print("Close the client socket")
                writer.close()

            def on_next(i):
                i.future.set_result(i.data)

            print("starting server")
            server = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
            loop.create_task(server)

            sink.subscribe(
                on_next=on_next,
                on_error=observer.on_error,
                on_completed=observer.on_completed)

        return reactivex.create(on_subscribe)


    loop = asyncio.get_event_loop()
    proxy = Subject()
    source = tcp_server(proxy, loop)
    aio_scheduler = AsyncIOScheduler(loop=loop)

    source.pipe(
        ops.map(lambda i: i._replace(data="echo: {}".format(i.data))),
        ops.delay(5.0)
    ).subscribe(proxy, scheduler=aio_scheduler)

    loop.run_forever()
    print("done")
    loop.close()


Execute this code from a shell, and connect to it via telnet. Then each line
that you type is echoed 5 seconds later. 

.. code:: console

    telnet localhost 8888
    Connected to localhost.
    Escape character is '^]'.
    foo
    echo: foo

If you connect simultaneously from several clients, you can see that requests
are correctly served, multiplexed on the AsyncIO event loop.

Default Scheduler
..................

There are several ways to choose a scheduler. The first one is to provide it
explicitly to each operator that supports a scheduler. However this can be
annoying when a lot of operators are used. So there is a second way to indicate
what scheduler will be used as the default scheduler for the whole chain: The
scheduler provided in the subscribe call is the default scheduler for all
operators in a pipe.

.. code:: python

    source.pipe(
        ...
    ).subscribe(proxy, scheduler=my_default_scheduler)

Operators that accept a scheduler select the scheduler to use in the following way:

- If a scheduler is provided for the operator, then use it.
- If a default scheduler is provided in subscribe, then use it.
- Otherwise use the default scheduler of the operator.
