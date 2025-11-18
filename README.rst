===============================
The ReactiveX for Python (RxPY)
===============================

.. image:: https://github.com/ReactiveX/RxPY/workflows/Python%20package/badge.svg
    :target: https://github.com/ReactiveX/RxPY/actions
    :alt: Build Status

.. image:: https://img.shields.io/coveralls/ReactiveX/RxPY.svg
    :target: https://coveralls.io/github/ReactiveX/RxPY
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/reactivex.svg
    :target: https://pypi.org/project/reactivex/
    :alt: PyPY Package Version

.. image:: https://img.shields.io/readthedocs/rxpy.svg
    :target: https://readthedocs.org/projects/rxpy/builds/
    :alt: Documentation Status


*A library for composing asynchronous and event-based programs using observable
collections and query operator functions in Python*

ReactiveX for Python v5
-----------------------

For v3.X please go to the `v3 branch
<https://github.com/ReactiveX/RxPY/tree/release/v3.2.x>`_.

ReactiveX for Python v4.x runs on `Python <http://www.python.org/>`_ 3.9 or above. To
install:

.. code:: console

    pip3 install reactivex


About ReactiveX
---------------

ReactiveX for Python (RxPY) is a library for composing asynchronous and event-based
programs using observable sequences and pipable query operators in Python. Using Rx,
developers represent asynchronous data streams with Observables, query asynchronous data
streams using operators, and parameterize concurrency in data/event streams using
Schedulers.

.. code:: python

    import reactivex as rx
    from reactivex import operators as ops

    source = rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    composed = source.pipe(
        ops.map(lambda s: len(s)),
        ops.filter(lambda i: i >= 5)
    )
    composed.subscribe(lambda value: print("Received {0}".format(value)))


Fluent and Functional Syntax
-----------------------------

RxPY supports both **fluent** (method chaining) and **functional** (pipe-based) syntax,
giving you the flexibility to choose the style that works best for your codebase:

**Fluent style** - Method chaining for a more Pythonic feel:

.. code:: python

    import reactivex as rx

    result = (rx.of(1, 2, 3, 4, 5)
        .map(lambda x: x * 2)
        .filter(lambda x: x > 5)
        .reduce(lambda acc, x: acc + x, 0)
    )
    result.subscribe(print)  # Output: 24

**Functional style** - Pipe-based for functional composition:

.. code:: python

    import reactivex as rx
    from reactivex import operators as ops

    result = rx.of(1, 2, 3, 4, 5).pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 5),
        ops.reduce(lambda acc, x: acc + x, 0)
    )
    result.subscribe(print)  # Output: 24

Both styles are **fully supported** and can even be mixed in the same pipeline.
Choose the style that best fits your team's preferences and coding standards.


Learning ReactiveX
------------------

Read the `documentation
<https://rxpy.readthedocs.io/en/latest/>`_ to learn
the principles of ReactiveX and get the complete reference of the available
operators.

If you need to migrate code from RxPY v1.x or v3.x, read the `migration
<https://rxpy.readthedocs.io/en/latest/migration.html>`_ section.

There is also a list of third party documentation available `here
<https://rxpy.readthedocs.io/en/latest/additional_reading.html>`_.


Community
----------

Join the conversation on GitHub `Discussions
<https://github.com/ReactiveX/RxPY/discussions>`_! if you have any questions or
suggestions.

Differences from .NET and RxJS
------------------------------

ReactiveX for Python is a fairly complete implementation of
`Rx <http://reactivex.io/>`_ with more than
`120 operators <https://rxpy.readthedocs.io/en/latest/operators.html>`_, and
over `1300 passing unit-tests <https://coveralls.io/github/ReactiveX/RxPY>`_. RxPY
is mostly a direct port of RxJS, but also borrows a bit from Rx.NET and RxJava in
terms of threading and blocking operators.

ReactiveX for Python follows `PEP 8 <http://legacy.python.org/dev/peps/pep-0008/>`_, so
all function and method names are ``snake_cased`` i.e lowercase with words separated by
underscores as necessary to improve readability.

Thus .NET code such as:

.. code:: c#

    var group = source.GroupBy(i => i % 3);


need to be written with an ``_`` in Python:

.. code:: python

    # Functional style
    group = source.pipe(ops.group_by(lambda i: i % 3))

    # Or fluent style
    group = source.group_by(lambda i: i % 3)

With ReactiveX for Python you should use `named keyword arguments
<https://docs.python.org/3/glossary.html>`_ instead of positional arguments when an
operator has multiple optional arguments. RxPY will not try to detect which arguments
you are giving to the operator (or not).

Development
-----------

This project is managed using `uv <https://docs.astral.sh/uv/>`_. Code is formatted
using `Ruff <https://github.com/astral-sh/ruff>`_. Code is statically type checked
using `pyright <https://github.com/microsoft/pyright>`_.

After cloning the repository, install dependencies:

.. code:: console

    uv sync

Run unit tests:

.. code:: console

    uv run pytest

Run type checking:

.. code:: console

    uv run pyright

Run code checks (manually):

.. code:: console

    uv run pre-commit run --all-files
