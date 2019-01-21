.. get_started

Get Started
============

An :class:`Observable <rx.Observable>` is the core type in ReactiveX. It
serially pushes items, known as *emissions*, through a series of operators until
it finally arrives at an :class:`Observer <rx.Observer>`, where they are
consumed.

Push-based (rather than pull-based) iteration opens up powerful new
possibilities to express code and concurrency much more quickly. Because an
:class:`Observable <rx.Observable>` treats events as data and data as events,
composing the two together becomes trivial.

There are many ways to create an :class:`Observable <rx.Observable>` that hands
items to an :class:`Observer <rx.Observer>`. You can use a :func:`create()
<rx.create>` factory and pass it a function that hands items to the
:class:`Observer <rx.Observer>`. The :class:`Observer <rx.Observer>` implements
:meth:`on_next() <rx.Observer.on_next>`, :meth:`on_completed()
<rx.Observer.on_completed>`, and :meth:`on_error() <rx.Observer.on_error>`
functions. The :meth:`on_next() <rx.Observer.on_next>` is used to pass items.
The :meth:`on_completed() <rx.Observer.on_completed>` will signal no more items
are coming, and the :meth:`on_error() <rx.Observer.on_error>` signals an error.

For instance, you can implement an :class:`Observer <rx.Observer>` with these three methods and
simply print these events. Then the `create()` can leverage a function that
passes five strings to the :class:`Observer <rx.Observer>` by calling those events.

.. code:: python

    from rx import Observer, create

    def push_five_strings(observer):
        observer.on_next("Alpha")
        observer.on_next("Beta")
        observer.on_next("Gamma")
        observer.on_next("Delta")
        observer.on_next("Epsilon")
        observer.on_completed()

    class PrintObserver(Observer):

        def on_next(self, value):
            print("Received {0}".format(value))

        def on_completed(self):
            print("Done!")

        def on_error(self, error):
            print("Error Occurred: {0}".format(error))

    source = create(push_five_strings)

    source.subscribe(PrintObserver())

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
iterates each emission as an :meth:`on_next() <rx.Observer.on_next>`, and then
calls :meth:`on_completed() <rx.Observer.on_completed>` when iteration is
complete. Therefore, we can simply pass these five Strings as arguments to it.

.. code:: python

    from rx import Observer

    class PrintObserver(Observer):

        def on_next(self, value):
            print("Received {0}".format(value))

        def on_completed(self):
            print("Done!")

        def on_error(self, error):
            print("Error Occurred: {0}".format(error))

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe(PrintObserver())


Most of the time you will not want to go through the verbosity of implementing
your own :class:`Observer <rx.Observer>`. You can instead pass 1 to 3 lambda
arguments to :meth:`subscribe() <rx.Observable.subscribe>` specifying the
:meth:`on_next() <rx.Observer.on_next>`, :meth:`on_completed()
<rx.Observer.on_completed>`, and :meth:`on_error()
<rx.Observer.on_error>` actions.

.. code:: python

    from rx import of

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe_(on_next=lambda value: print("Received {0}".format(value)),
                    on_completed=lambda: print("Done!"),
                    on_error=lambda error: print("Error Occurred: {0}".format(error))
                    )

You do not have to specify all three events types. You can pick and choose which
events you want to observe using the named arguments, or simply provide a single
lambda for the :meth:`on_next() <rx.Observer.on_next>`. Typically in production,
you will want to provide an :meth:`on_error() <rx.Observer.on_error>` so errors
are explicitly handled by the subscriber.

.. code:: python

    from rx import of

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    source.subscribe_(lambda value: print("Received {0}".format(value)))

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
    composed.subscribe_(lambda value: print("Received {0}".format(value)))

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
    ).subscribe_(lambda value: print("Received {0}".format(value)))

Custom operator
---------------

Concurrency
-----------

To achieve concurrency, you use two operators: :func:`subscribe_on()
<rx.operators.subscribe_on>` and :func:`observe_on() <rx.operators.observe_on>`.
Both need a *Scheduler* which provides a thread for each subscription to do work
(see section on Schedulers below). The :class:`ThreadPoolScheduler
<rx.concurrency.ThreadPoolScheduler>` is a good choice to create a pool of reusable
worker threads.

.. attention::

    [GIL](https://wiki.python.org/moin/GlobalInterpreterLock) has the potential to
    undermine your concurrency performance, as it prevents multiple threads from
    accessing the same line of code simultaneously. Libraries like
    [NumPy](http://www.numpy.org/) can mitigate this for parallel intensive
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
        .subscribe_(on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
                    on_error=lambda e: print(e),
                    on_completed=lambda: print("PROCESS 1 done!"))

    # Create Process 2
    Observable.range(1, 10) \
        .map(lambda s: intense_calculation(s)) \
        .subscribe_on(pool_scheduler) \
        .subscribe_(on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
                    on_error=lambda e: print(e), on_completed=lambda: print("PROCESS 2 done!"))

    # Create Process 3, which is infinite
    Observable.interval(1000) \
        .map(lambda i: i * 100) \
        .observe_on(pool_scheduler) \
        .map(lambda s: intense_calculation(s)) \
        .subscribe_(on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
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

