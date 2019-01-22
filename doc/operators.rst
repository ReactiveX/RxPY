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

=========================================   ================================================
Operator                                                    Description
=========================================   ================================================
:func:`buffer <rx.operators.buffer>`        periodically gather items from an Observable into bundles and emit these bundles rather than emitting the items one at a time
:func:`flat_map <rx.operators.flat_map>`    transform the items emitted by an Observable into Observables, then flatten the emissions from those into a single Observable
:func:`group_by <rx.operators.group_by>`    divide an Observable into a set of Observables that each emit a different group of items from the original Observable, organized by key
:func:`map <rx.operators.map>`              transform the items emitted by an Observable by applying a function to each item
:func:`scan <rx.operators.scan>`            apply a function to each item emitted by an Observable, sequentially, and emit each successive value
:func:`window <rx.operators.window>`        periodically subdivide items from an Observable into Observable windows and emit these windows rather than emitting the items one at a time
=========================================   ================================================

Filtering Observables
----------------------

======================================================  ================================================
Operator                                                                Description
======================================================  ================================================
:func:`debounce <rx.operators.debounce>`                only emit an item from an Observable if a particular timespan has passed without it emitting another item
:func:`distinct <rx.operators.distinct>`                suppress duplicate items emitted by an Observable
:func:`element_at <rx.operators.element_at>`            emit only item n emitted by an Observable
:func:`filter <rx.operators.filter>`                    emit only those items from an Observable that pass a predicate test
:func:`first <rx.operators.first>`                      emit only the first item, or the first item that meets a condition, from an Observable
:func:`ignore_elements <rx.operators.ignore_elements>`  do not emit any items from an Observable but mirror its termination notification
:func:`last <rx.operators.last>`                        emit only the last item emitted by an Observable
:func:`sample <rx.operators.sample>`                    emit the most recent item emitted by an Observable within periodic time intervals
:func:`skip <rx.operators.skip>`                        suppress the first n items emitted by an Observable
:func:`skip_last <rx.operators.skip_last>`              suppress the last n items emitted by an Observable
:func:`take <rx.operators.take>`                        emit only the first n items emitted by an Observable
:func:`take_last <rx.operators.take_last>`              emit only the last n items emitted by an Observable
======================================================  ================================================

Combining Observables
----------------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`combine_latest <rx.operators.combine_latest>`    when an item is emitted by either of two Observables, combine the latest item emitted by each Observable via a specified function and emit items based on the results of this function
:func:`join <rx.operators.join>`                        combine items emitted by two Observables whenever an item from one Observable is emitted during a time window defined according to an item emitted by the other Observable
:func:`merge <rx.operators.merge>`                      combine multiple Observables into one by merging their emissions
:func:`start_with <rx.operators.start_with>`            emit a specified sequence of items before beginning to emit the items from the source Observable
:func:`switch_latest <rx.operators.switch_latest>`      convert an Observable that emits Observables into a single Observable that emits the items emitted by the most-recently-emitted of those Observables
:func:`zip <rx.operators.zip>`                          combine the emissions of multiple Observables together via a specified function and emit single items for each combination based on the results of this function
======================================================  ================================================

Error Handling
---------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`catch_exception <rx.operators.catch_exception>`  recover from an onError notification by continuing the sequence without error
:func:`retry <rx.operators.retry>`                      if a source Observable sends an onError notification, resubscribe to it in the hopes that it will complete without error
======================================================  ================================================

Utility Operators
------------------

======================================================  ================================================
Operator                                                                    Description
======================================================  ================================================
:func:`delay <rx.operators.delay>`                      shift the emissions from an Observable forward in time by a particular amount
:func:`do <rx.operators.do>`                            register an action to take upon a variety of Observable lifecycle events
:func:`materialize <rx.operators.materialize>`          Materializes the implicit notifications of an observable sequence as explicit notification values.
:func:`dematerialize <rx.operators.dematerialize>`      Dematerializes the explicit notification values of an observable sequence as implicit notifications.
:func:`observe_on <rx.operators.observe_on>`            specify the scheduler on which an observer will observe this Observable
:meth:`subscribe <rx.Observable.subscribe>`             operate upon the emissions and notifications from an Observable
:func:`subscribe_on <rx.operators.subscribe_on>`        specify the scheduler an Observable should use when it is subscribed to
:func:`time_interval <rx.operators.time_interval>`      convert an Observable that emits items into one that emits indications of the amount of time elapsed between those emissions
:func:`timeout <rx.operators.timeout>`                  mirror the source Observable, but issue an error notification if a particular period of time elapses without any emitted items
:func:`timestamp <rx.operators.timestamp>`              attach a timestamp to each item emitted by an Observable
======================================================  ================================================

Conditional and Boolean Operators
----------------------------------

==========================================================  ================================================
Operator                                                                        Description
==========================================================  ================================================
:func:`all <rx.operators.all>`                              determine whether all items emitted by an Observable meet some criteria
:func:`amb <rx.operators.amb>`                              given two or more source Observables, emit all of the items from only the first of these Observables to emit an item
:func:`contains <rx.operators.contains>`                    determine whether an Observable emits a particular item or not
:func:`default_if_empty <rx.operators.default_if_empty>`    emit items from the source Observable, or a default item if the source Observable emits nothing
:func:`sequence_equal <rx.operators.sequence_equal>`        determine whether two Observables emit the same sequence of items
:func:`skip_until <rx.operators.skip_until>`                discard items emitted by an Observable until a second Observable emits an item
:func:`skip_while <rx.operators.skip_while>`                discard items emitted by an Observable until a specified condition becomes false
:func:`take_until <rx.operators.take_until>`                discard items emitted by an Observable after a second Observable emits an item or terminates
:func:`take_whle <rx.operators.take_while>`                 discard items emitted by an Observable after a specified condition becomes false
==========================================================  ================================================

Mathematical and Aggregate Operators
-------------------------------------

=========================================   ================================================
Operator                                                    Description
=========================================   ================================================
:func:`average <rx.operators.average>`      calculates the average of numbers emitted by an Observable and emits this average
:func:`concat <rx.operators.concat>`        emit the emissions from two or more Observables without interleaving them
:func:`count <rx.operators.count>`          count the number of items emitted by the source Observable and emit only this value
:func:`max <rx.operators.max>`              determine, and emit, the maximum-valued item emitted by an Observable
:func:`min <rx.operators.min>`              determine, and emit, the minimum-valued item emitted by an Observable
:func:`reduce <rx.operators.reduce>`        apply a function to each item emitted by an Observable, sequentially, and emit the final value
:func:`sum <rx.operators.sum>`              calculate the sum of numbers emitted by an Observable and emit this sum
=========================================   ================================================

Connectable Observable Operators
---------------------------------

=====================================================   ================================================
Operator                                                                Description
=====================================================   ================================================
:meth:`connect <rx.ConnectableObservable.connect>`      instruct a connectable Observable to begin emitting items to its subscribers
:func:`publish <rx.operators.publish>`                  convert an ordinary Observable into a connectable Observable
:func:`ref_count <rx.operators.ref_count>`              make a Connectable Observable behave like an ordinary Observable
:func:`replay <rx.operators.replay>`                    ensure that all observers see the same sequence of emitted items, even if they subscribe after the Observable has begun emitting items
=====================================================   ================================================
