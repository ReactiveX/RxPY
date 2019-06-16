.. _operators:

Operators
==========

Creating Observables
---------------------


======================================  ================================================
Operator                                            Description
======================================  ================================================
:func:`create <rx.create>`              Create an Observable from scratch by calling observer methods programmatically.
:func:`empty <rx.empty>`                Creates an Observable that emits no item and completes immediately.
:func:`never <rx.never>`                Creates an Observable that never completes.
:func:`throw <rx.throw>`                Creates an Observable that terminates with an error.
:func:`from_ <rx.from_>`                Convert some other object or data structure into an Observable.
:func:`interval <rx.interval>`          Create an Observable that emits a sequence of integers spaced by a particular time interval.
:func:`just <rx.just>`                  Convert an object or a set of objects into an Observable that emits that object or those objects.
:func:`range <rx.range>`                Create an Observable that emits a range of sequential integers.
:func:`repeat_value <rx.repeat_value>`  Create an Observable that emits a particular item or sequence of items repeatedly.
:func:`start <rx.start>`                Create an Observable that emits the return value of a function.
:func:`timer <rx.timer>`                Create an Observable that emits a single item after a given delay.
======================================  ================================================

Transforming Observables
------------------------

=========================================   ================================================
Operator                                                    Description
=========================================   ================================================
:func:`buffer <rx.operators.buffer>`        Periodically gather items from an Observable into bundles and emit these bundles rather than emitting the items one at a time.
:func:`flat_map <rx.operators.flat_map>`    Transform the items emitted by an Observable into Observables, then flatten the emissions from those into a single Observable.
:func:`group_by <rx.operators.group_by>`    Divide an Observable into a set of Observables that each emit a different group of items from the original Observable, organized by key.
:func:`map <rx.operators.map>`              Transform the items emitted by an Observable by applying a function to each item.
:func:`scan <rx.operators.scan>`            Apply a function to each item emitted by an Observable, sequentially, and emit each successive value.
:func:`window <rx.operators.window>`        Periodically subdivide items from an Observable into Observable windows and emit these windows rather than emitting the items one at a time.
=========================================   ================================================

Filtering Observables
----------------------

======================================================  ================================================
Operator                                                                Description
======================================================  ================================================
:func:`debounce <rx.operators.debounce>`                Only emit an item from an Observable if a particular timespan has passed without it emitting another item.
:func:`distinct <rx.operators.distinct>`                Suppress duplicate items emitted by an Observable.
:func:`element_at <rx.operators.element_at>`            Emit only item n emitted by an Observable.
:func:`filter <rx.operators.filter>`                    Emit only those items from an Observable that pass a predicate test.
:func:`first <rx.operators.first>`                      Emit only the first item, or the first item that meets a condition, from an Observable.
:func:`ignore_elements <rx.operators.ignore_elements>`  Do not emit any items from an Observable but mirror its termination notification.
:func:`last <rx.operators.last>`                        Emit only the last item emitted by an Observable.
:func:`sample <rx.operators.sample>`                    Emit the most recent item emitted by an Observable within periodic time intervals.
:func:`skip <rx.operators.skip>`                        Suppress the first n items emitted by an Observable.
:func:`skip_last <rx.operators.skip_last>`              Suppress the last n items emitted by an Observable.
:func:`take <rx.operators.take>`                        Emit only the first n items emitted by an Observable.
:func:`take_last <rx.operators.take_last>`              Emit only the last n items emitted by an Observable.
======================================================  ================================================

Combining Observables
----------------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`combine_latest <rx.operators.combine_latest>`    When an item is emitted by either of two Observables, combine the latest item emitted by each Observable via a specified function and emit items based on the results of this function.
:func:`join <rx.operators.join>`                        Combine items emitted by two Observables whenever an item from one Observable is emitted during a time window defined according to an item emitted by the other Observable.
:func:`merge <rx.operators.merge>`                      Combine multiple Observables into one by merging their emissions.
:func:`start_with <rx.operators.start_with>`            Emit a specified sequence of items before beginning to emit the items from the source Observable.
:func:`switch_latest <rx.operators.switch_latest>`      Convert an Observable that emits Observables into a single Observable that emits the items emitted by the most-recently-emitted of those Observables.
:func:`zip <rx.operators.zip>`                          Combine the emissions of multiple Observables together via a specified function and emit single items for each combination based on the results of this function.
======================================================  ================================================

Error Handling
---------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`catch_exception <rx.operators.catch_exception>`  Recover from an onError notification by continuing the sequence without error.
:func:`retry <rx.operators.retry>`                      If a source Observable sends an onError notification, resubscribe to it in the hopes that it will complete without error.
======================================================  ================================================

Utility Operators
------------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`delay <rx.operators.delay>`                      Shift the emissions from an Observable forward in time by a particular amount.
:func:`do <rx.operators.do>`                            Register an action to take upon a variety of Observable lifecycle events.
:func:`materialize <rx.operators.materialize>`          Materializes the implicit notifications of an observable sequence as explicit notification values.
:func:`dematerialize <rx.operators.dematerialize>`      Dematerializes the explicit notification values of an observable sequence as implicit notifications.
:func:`observe_on <rx.operators.observe_on>`            Specify the scheduler on which an observer will observe this Observable.
:meth:`subscribe <rx.Observable.subscribe>`             Operate upon the emissions and notifications from an Observable.
:func:`subscribe_on <rx.operators.subscribe_on>`        Specify the scheduler an Observable should use when it is subscribed to.
:func:`time_interval <rx.operators.time_interval>`      Convert an Observable that emits items into one that emits indications of the amount of time elapsed between those emissions.
:func:`timeout <rx.operators.timeout>`                  Mirror the source Observable, but issue an error notification if a particular period of time elapses without any emitted items.
:func:`timestamp <rx.operators.timestamp>`              Attach a timestamp to each item emitted by an Observable.
======================================================  ================================================

Conditional and Boolean Operators
----------------------------------

==========================================================  ================================================
Operator                                                                        Description
==========================================================  ================================================
:func:`all <rx.operators.all>`                              Determine whether all items emitted by an Observable meet some criteria.
:func:`amb <rx.operators.amb>`                              Given two or more source Observables, emit all of the items from only the first of these Observables to emit an item.
:func:`contains <rx.operators.contains>`                    Determine whether an Observable emits a particular item or not.
:func:`default_if_empty <rx.operators.default_if_empty>`    Emit items from the source Observable, or a default item if the source Observable emits nothing.
:func:`sequence_equal <rx.operators.sequence_equal>`        Determine whether two Observables emit the same sequence of items.
:func:`skip_until <rx.operators.skip_until>`                Discard items emitted by an Observable until a second Observable emits an item.
:func:`skip_while <rx.operators.skip_while>`                Discard items emitted by an Observable until a specified condition becomes false.
:func:`take_until <rx.operators.take_until>`                Discard items emitted by an Observable after a second Observable emits an item or terminates.
:func:`take_whle <rx.operators.take_while>`                 Discard items emitted by an Observable after a specified condition becomes false.
==========================================================  ================================================

Mathematical and Aggregate Operators
-------------------------------------

=========================================   ================================================
Operator                                                    Description
=========================================   ================================================
:func:`average <rx.operators.average>`      Calculates the average of numbers emitted by an Observable and emits this average.
:func:`concat <rx.operators.concat>`        Emit the emissions from two or more Observables without interleaving them.
:func:`count <rx.operators.count>`          Count the number of items emitted by the source Observable and emit only this value.
:func:`max <rx.operators.max>`              Determine, and emit, the maximum-valued item emitted by an Observable.
:func:`min <rx.operators.min>`              Determine, and emit, the minimum-valued item emitted by an Observable.
:func:`reduce <rx.operators.reduce>`        Apply a function to each item emitted by an Observable, sequentially, and emit the final value.
:func:`sum <rx.operators.sum>`              Calculate the sum of numbers emitted by an Observable and emit this sum.
=========================================   ================================================

Connectable Observable Operators
---------------------------------

=====================================================   ================================================
Operator                                                                Description
=====================================================   ================================================
:meth:`connect <rx.ConnectableObservable.connect>`      Instruct a connectable Observable to begin emitting items to its subscribers.
:func:`publish <rx.operators.publish>`                  Convert an ordinary Observable into a connectable Observable.
:func:`ref_count <rx.operators.ref_count>`              Make a Connectable Observable behave like an ordinary Observable.
:func:`replay <rx.operators.replay>`                    Ensure that all observers see the same sequence of emitted items, even if they subscribe after the Observable has begun emitting items.
=====================================================   ================================================
