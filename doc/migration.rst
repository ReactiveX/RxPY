.. _migration:

Migration
=========

RxPY v3 is a major evolution from RxPY v1. This release brings many
improvements, some of the most important ones being:

* A better integration in IDEs via autocompletion support.
* New operators can be implemented outside of RxPY.
* Operator chains are now built via the *pipe* operator.
* A default scheduler can be provided in an operator chain.

Pipe Based Operator Chaining
-----------------------------

The most fundamental change is the way operators are chained together. On RxPY
v1, operators were methods of the Observable class. So they were chained by
using the existing Observable methods:

.. code:: python

    from rx import Observable

    Observable.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon") \
        .map(lambda s: len(s)) \
        .filter(lambda i: i >= 5) \
        .subscribe(lambda value: print("Received {0}".format(value)))

Chaining in RxPY v3 is based on the pipe operator. This pipe operator is now one
of the only methods of the Observable class. In RxPY v3, operators are
implemented as functions:

.. code:: python

    from rx import of, operators as op

    of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
            op.map(lambda s: len(s)),
            op.filter(lambda i: i >= 5)
        ).subscribe_(lambda value: print("Received {0}".format(value)))

The fact that operators are functions means that adding new operators is now
very easy. Instead of wrapping custom operators with the *let* operator, they can
be directly used in a pipe chain.

Removal Of The Result Mapper 
-----------------------------

The mapper function is removed in operators that combine the values of several
observables. This change applies to the following operators: zip,
zip_with_iterable, join, group_join, combine_latest, and with_latest_from.

In RxPY v1, these operators were used the following way:

.. code:: python

    from rx import Observable
    import operator

    a = Observable.of(1, 2, 3, 4)
    b = Observable.of(2, 2, 4, 4)

    a.zip(b, lambda a, b: operator.mul(a, b)) \
        .subscribe(print)

Now they return an Observable of tuples, with each item being the combination of
the source Observables:

.. code:: python

    from rx import of, operators as op
    import operator

    a = of(1, 2, 3, 4)
    b = of(2, 2, 4, 4)

    a.pipe(
        op.zip(b), # returns a tuple with the items of a and b
        op.map(lambda z: operator.mul(z[0], z[1]))
    ).subscribe(print)

Dealing with the tuple unpacking is made easier with the starmap operator that
unpacks the tuple to args:

.. code:: python

    from rx import of, operators as op
    import operator

    a = of(1, 2, 3, 4)
    b = of(2, 2, 4, 4)

    a.pipe(
        op.zip(b),
        op.starmap(operator.mul)
    ).subscribe(print)


Scheduler Parameter In Create Operator
---------------------------------------

subscription function takes two parameters: observer and scheduler

Removal Of List Of Observables
-------------------------------

merge, zip, combine_latest... take only observable arguments, no lists.

Time Is In Seconds
------------------

Operators that take time values as parameters now use seconds as a unit instead
of milliseconds:

.. code:: python

    obs.debounce(500)

is now written as:

.. code:: python

    obs.debounce(0.5)