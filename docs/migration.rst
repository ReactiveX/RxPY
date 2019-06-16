.. _migration:

Migration
=========

RxPY v3 is a major evolution from RxPY v1. This release brings many
improvements, some of the most important ones being:

* A better integration in IDEs via autocompletion support.
* New operators can be implemented outside of RxPY.
* Operator chains are now built via the :func:`pipe <rx.Observable.pipe>` operator.
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

Chaining in RxPY v3 is based on the :func:`pipe <rx.Observable.pipe>` operator.
This operator is now one of the only methods of the
:class:`Observable <rx.Observable>` class. In RxPY v3, operators are implemented
as functions:

.. code:: python

    import rx
    from rx import operators as ops

    rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        ops.map(lambda s: len(s)),
        ops.filter(lambda i: i >= 5)
    ).subscribe(lambda value: print("Received {0}".format(value)))

The fact that operators are functions means that adding new operators is now
very easy. Instead of wrapping custom operators with the *let* operator, they can
be directly used in a pipe chain.

Removal Of The Result Mapper
-----------------------------

The mapper function is removed in operators that combine the values of several
observables. This change applies to the following operators:
:func:`combine_latest <rx.operators.combine_latest>`,
:func:`group_join <rx.operators.group_join>`,
:func:`join <rx.operators.join>`,
:func:`with_latest_from <rx.operators.with_latest_from>`,
:func:`zip <rx.operators.zip>`, and
:func:`zip_with_iterable <rx.operators.zip_with_iterable>`.

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

    import rx
    from rx import operators as ops
    import operator

    a = rx.of(1, 2, 3, 4)
    b = rx.of(2, 2, 4, 4)

    a.pipe(
        ops.zip(b), # returns a tuple with the items of a and b
        ops.map(lambda z: operator.mul(z[0], z[1]))
    ).subscribe(print)

Dealing with the tuple unpacking is made easier with the starmap operator that
unpacks the tuple to args:

.. code:: python

    import rx
    from rx import operators as ops
    import operator

    a = rx.of(1, 2, 3, 4)
    b = rx.of(2, 2, 4, 4)

    a.pipe(
        ops.zip(b),
        ops.starmap(operator.mul)
    ).subscribe(print)


Scheduler Parameter In Create Operator
---------------------------------------

The subscription function provided to the :func:`create <rx.create>` operator
now takes two parameters: An observer and a scheduler. The scheduler parameter
is new: If a scheduler has been set in the call to subscribe, then this
scheduler is passed to the subscription function. Otherwise this parameter is
set to *None*.

One can use or ignore this parameter. This new scheduler parameter allows the
create operator to use the default scheduler provided in the subscribe call. So
scheduling item emissions with relative or absolute due-time is now possible.


Removal Of List Of Observables
-------------------------------

The support of list of Observables as a parameter has been removed in the
following operators:
:func:`merge <rx.merge>`,
:func:`zip <rx.zip>`, and
:func:`combine_latest <rx.combine_latest>`.
For example in RxPY v1 the *merge* operator could be called with a list:

.. code:: python

    from rx import Observable

    obs1 = Observable.from_([1, 2, 3, 4])
    obs2 = Observable.from_([5, 6, 7, 8])

    res = Observable.merge([obs1, obs2])
    res.subscribe(print)

This is not possible anymore in RxPY v3. So Observables must be provided
explicitly:

.. code:: python

    import rx, operator as op

    obs1 = rx.from_([1, 2, 3, 4])
    obs2 = rx.from_([5, 6, 7, 8])

    res = rx.merge(obs1, obs2)
    res.subscribe(print)

If for any reason the Observables are only available as a list, then they can be
unpacked:

.. code:: python

    import rx
    from rx import operators as ops

    obs1 = rx.from_([1, 2, 3, 4])
    obs2 = rx.from_([5, 6, 7, 8])

    obs_list = [obs1, obs2]

    res = rx.merge(*obs_list)
    res.subscribe(print)



Blocking Observable
-------------------

BlockingObservables have been removed from RxPY v3. In RxPY v1, blocking until
an Observable completes was done the following way:

.. code:: python

    from rx import Observable

    res = Observable.from_([1, 2, 3, 4]).to_blocking().last()
    print(res)

This is now done with the :func:`run <rx.Observable.run>` operator:

.. code:: python

    import rx

    res = rx.from_([1, 2, 3, 4]).run()
    print(res)

The *run* operator returns only the last value emitted by the source
Observable. It is possible to use the previous blocking operators by using the
standard operators before *run*. For example:

* Get first item: obs.pipe(ops.first()).run()
* Get all items: obs.pipe(ops.to_list()).run()


Back-Pressure
--------------

Support for back-pressure - and so ControllableObservable - has been removed in
RxPY v3. Back-pressure can be implemented in several ways, and many strategies
can be adopted. So we consider that such features are beyond the scope of RxPY.
You are encouraged to provide independent implementations as separate packages
so that they can be shared by the community.

List of community projects supporting backpressure can be found in
:ref:`additional_readings`.

Time Is In Seconds
------------------

Operators that take time values as parameters now use seconds as a unit instead
of milliseconds. This RxPY v1 example:

.. code:: python

    ops.debounce(500)

is now written as:

.. code:: python

    ops.debounce(0.5)

Packages Renamed
----------------

Some packages were renamed:

+-----------------------+-------------------------+
| Old name              | New name                |
+-----------------------+-------------------------+
| *rx.concurrency*      | *rx.scheduler*          |
+-----------------------+-------------------------+
| *rx.disposables*      | *rx.disposable*         |
+-----------------------+-------------------------+
| *rx.subjects*         | *rx.subject*            |
+-----------------------+-------------------------+

Furthermore, the package formerly known as *rx.concurrency.mainloopscheduler*
has been split into two parts, *rx.scheduler.mainloop* and
*rx.scheduler.eventloop*.
