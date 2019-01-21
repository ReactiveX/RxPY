.. _operators:

Operators
==========

Creating Observables
---------------------


======================================  ================================================
Operator                                            Description
======================================  ================================================
:func:`create <rx.create>`              create an Observable from scratch by calling observer methods programmatically
:func:`empty <rx.empty>`                creates an Observable that emits no item and completes immediatly
:func:`never <rx.never>`                creates an Observable that never completes
:func:`throw <rx.throw>`                creates an Observable that raises an error containing an exception
:func:`from_ <rx.from_>`                convert some other object or data structure into an Observable
:func:`interval <rx.interval>`          create an Observable that emits a sequence of integers spaced by a particular time interval
:func:`just <rx.just>`                  convert an object or a set of objects into an Observable that emits that or those objects
:func:`range <rx.range>`                create an Observable that emits a range of sequential integers
:func:`repeat_value <rx.repeat_value>`  create an Observable that emits a particular item or sequence of items repeatedly
:func:`start <rx.start>`                create an Observable that emits the return value of a function
:func:`timer <rx.timer>`                create an Observable that emits a single item after a given delay
======================================  ================================================

Transforming Observables
------------------------

Filtering Observables
----------------------

Combining Observables
----------------------

Error Handling
---------------

Utility Operators
------------------

Conditional and Boolean Operators
----------------------------------

Mathematical and Aggregate Operators
-------------------------------------

Connectable Observable Operators
---------------------------------

Operators to Convert Observables
---------------------------------