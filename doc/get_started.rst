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

This example gives the following result:

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

This example gives the following result:

.. code:: console

    Received Alpha
    Received Beta
    Received Gamma
    Received Delta
    Received Epsilon
