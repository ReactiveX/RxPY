==========================================
The Reactive Extensions for Python (RxPY)
==========================================

.. image:: https://img.shields.io/travis/ReactiveX/RxPY.svg
        :target: https://travis-ci.org/ReactiveX/RxPY

.. image:: https://img.shields.io/coveralls/ReactiveX/RxPY.svg
        :target: https://coveralls.io/github/ReactiveX/RxPY

.. image:: https://img.shields.io/pypi/v/rx.svg
        :target: https://pypi.python.org/pypi/Rx

.. image:: https://img.shields.io/readthedocs/rxpy.svg
        :target: https://readthedocs.org/projects/rxpy/builds/
        :alt: Documentation Status


*A library for composing asynchronous and event-based programs using observable collections and
query operator functions in Python*

RxPY v3.0 Alpha
----------------

**This branch is work-in-progress.**

FOR V 1.X PLEASE GO TO `STABLE BRANCH <https://github.com/ReactiveX/RxPY/tree/release/v1.6.x>`_.

RxPY v3.x runs on `Python <http://www.python.org/>`_ 3.6 or above. To install
RxPY:

.. code:: console

    pip3 install --pre rx


About ReactiveX
------------------

Reactive Extensions for Python (RxPY) is a set of libraries for composing
asynchronous and event-based programs using observable sequences and pipable
query operators in Python. Using Rx, developers represent asynchronous data
streams with Observables, query asynchronous data streams using operators, and
parameterize concurrency in data/event streams using Schedulers.

.. code:: python

    from rx import of, operators as op

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    composed = source.pipe(
        op.map(lambda s: len(s)),
        op.filter(lambda i: i >= 5)
    )
    composed.subscribe_(lambda value: print("Received {0}".format(value)))


Learning RxPY
--------------

Read the `documentation
<https://github.com/ReactiveX/RxPY/tree/master/doc/get_started.rst>`_ to learn
the principles of RxPY and get the complete reference of the available
operators.

I you need to migrate code from RxPY v1.x, read the `migration
<https://github.com/ReactiveX/RxPY/blob/master/doc/migration.rst>`_ section.

There is also a list of third party documentation available `here
<https://github.com/ReactiveX/RxPY/blob/master/doc/additional_readings.rst>`_.


Community
----------

Join the conversation on Slack!

The gracious folks at `PySlackers <https://pyslackers.com/>`_ have given us a home
in the `#rxpy <https://pythondev.slack.com/messages/rxpy>`_ Slack channel. Please
join us there for questions, conversations, and all things related to RxPy.

To join, navigate the page above to receive an email invite. After signing up,
join us in the #rxpy channel.

Please follow the community guidelines and terms of service.


Differences from .NET and RxJS
------------------------------

RxPY is a fairly complete implementation of
`Rx <http://reactivex.io/>`_ with more than
`134 query operators <http://reactivex.io/documentation/operators.html>`_, and
over `1100 passing unit-tests <https://coveralls.io/github/dbrattli/RxPY>`_. RxPY
is mostly a direct port of RxJS, but also borrows a bit from RxNET and RxJava in
terms of threading and blocking operators.

RxPY follows `PEP 8 <http://legacy.python.org/dev/peps/pep-0008/>`_, so all
function and method names are lowercase with words separated by underscores as
necessary to improve readability.

Thus .NET code such as:

.. code:: c#

    var group = source.GroupBy(i => i % 3);


need to be written with an `_` in Python:

.. code:: python

    group = source.group_by(lambda i: i % 3)

With RxPY you should use `named keyword arguments
<https://docs.python.org/3/glossary.html>`_ instead of positional arguments when
an operator has multiple optional arguments. RxPY will not try to detect which
arguments you are giving to the operator (or not).
