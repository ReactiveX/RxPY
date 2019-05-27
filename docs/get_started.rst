.. get_started

Get Started
============

An :class:`Observable <rx.Observable>` is the core type in ReactiveX. It
serially pushes items, known as *emissions*, through a series of operators until
it finally arrives at an Observer, where they are
consumed.

Push-based (rather than pull-based) iteration opens up powerful new
possibilities to express code and concurrency much more quickly. Because an
:class:`Observable <rx.Observable>` treats events as data and data as events,
composing the two together becomes trivial.

There are many ways to create an :class:`Observable <rx.Observable>` that hands
items to an Observer. You can use a :func:`create()
<rx.create>` factory and pass it functions that handle items:

* The *on_next* function is called each time the Observable emits an item.
* The *on_completed* function is called when the Observable completes.
* The *on_error* function is called when an error occurs on the Observable.

You do not have to specify all three events types. You can pick and choose which
events you want to observe by providing only some of the callbacks, or simply by
providing a single lambda for *on_next*. Typically in production, you will want
to provide an *on_error* handler so that errors are explicitly handled by the
subscriber.

Let's consider the following example:

.. code:: python

    from rx import create

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
five items, we can rid the :func:`create() <rx.create>` and its backing
function, and use :func:`of() <rx.of>`. This factory accepts an argument list,
iterates on each argument to emit them as items, and the completes. Therefore,
we can simply pass these five Strings as arguments to it:

.. code:: python

    from rx import of

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe(
        on_next = lambda i: print("Received {0}".format(i)),
        on_error = lambda e: print("Error Occurred: {0}".format(e)),
        on_completed = lambda: print("Done!"),
    )

And a single parameter can be provided to the subscribe function if completion
and error are ignored:

.. code:: python

    from rx import of

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
Each operator will yield a new :class:`Observable <rx.Observable>` that
transforms emissions from the source in some way. For example, we can
:func:`map() <rx.operators.map>` each `String` to its length, then
:func:`filter() <rx.operators.filter>` for lengths being at least 5. These will
yield two separate Observables built off each other.

.. code:: python

    from rx import of, operators as op

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

    from rx import of, operators as op

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

    import rx
    from rx import operators as ops

    def length_more_than_5():
        return pipe(
            ops.map(lambda s: len(s)),
            ops.filter(lambda i: i >= 5),
        )

    rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        length_more_than_5()
    ).subscribe(lambda value: print("Received {0}".format(value)))

In this example, the *pipe* and *filter* operators are grouped in a new
*length_more_then_5* operator.

It is also possible to create an operator that is not a composition of other
operators. This allows to fully control the subscription logic and items
emissions:

 .. code:: python

    import rx

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
            return rx.create(subscribe)
        return _lowercase

    rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
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
<rx.operators.subscribe_on>` and :func:`observe_on() <rx.operators.observe_on>`.
Both need a :ref:`Scheduler <reference_scheduler>` which provides a thread for
each subscription to do work (see section on Schedulers below). The
:class:`ThreadPoolScheduler <rx.concurrency.ThreadPoolScheduler>` is a good
choice to create a pool of reusable worker threads.

.. attention::

    `GIL <https://wiki.python.org/moin/GlobalInterpreterLock>`_ has the potential to
    undermine your concurrency performance, as it prevents multiple threads from
    accessing the same line of code simultaneously. Libraries like
    `NumPy <http://www.numpy.org/>`_ can mitigate this for parallel intensive
    computations as they free the GIL. RxPy may also minimize thread overlap to some
    degree. Just be sure to test your application with concurrency and ensure there
    is a performance gain.

The :func:`subscribe_on() <rx.operators.subscribe_on>` instructs the source
:class:`Observable <rx.Observable>` at the start of the chain which scheduler to
use (and it does not matter where you put this operator). The
:func:`observe_on() <rx.operators.observe_on>`, however, will switch to a
different *Scheduler* **at that point** in the *Observable* chain, effectively
moving an emission from one thread to another. Some :ref:`Observable factories
<reference_observable_factory>` and :ref:`operators
<reference_operators>`, like :func:`interval() <rx.interval>` and
:func:`delay() <rx.operators.delay>`, already have a default *Scheduler* and
thus will ignore any :func:`subscribe_on() <rx.operators.subscribe_on>` you
specify (although you can pass a *Scheduler* usually as an argument).

Below, we run three different processes concurrently rather than sequentially
using :func:`subscribe_on() <rx.operators.subscribe_on>` as well as an
:func:`observe_on() <rx.operators.observe_on>`.

.. code:: python

    import multiprocessing
    import random
    import time
    from threading import current_thread

    from rx import Observable
    from rx.concurrency import ThreadPoolScheduler


    def intense_calculation(value):
        # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
        time.sleep(random.randint(5, 20) * .1)
        return value

    # calculate number of CPU's, then create a ThreadPoolScheduler with that number of threads
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    # Create Process 1
    Observable.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon") \
        .map(lambda s: intense_calculation(s)) \
        .subscribe_on(pool_scheduler) \
        .subscribe(on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
                    on_error=lambda e: print(e),
                    on_completed=lambda: print("PROCESS 1 done!"))

    # Create Process 2
    Observable.range(1, 10) \
        .map(lambda s: intense_calculation(s)) \
        .subscribe_on(pool_scheduler) \
        .subscribe(on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
                    on_error=lambda e: print(e), on_completed=lambda: print("PROCESS 2 done!"))

    # Create Process 3, which is infinite
    Observable.interval(1000) \
        .map(lambda i: i * 100) \
        .observe_on(pool_scheduler) \
        .map(lambda s: intense_calculation(s)) \
        .subscribe(on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
                    on_error=lambda e: print(e))

    input("Press any key to exit\n")

**OUTPUT:**

.. code:: console

    Press any key to exit
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


Default Scheduler
..................
