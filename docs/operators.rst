.. _operators:

Operators
==========

These tables list the pipeable operators in :mod:`reactivex.operators`.
See the :doc:`operator API reference <reference_operators>` for signatures
and detailed descriptions.

Creating Observables
---------------------


.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`create <reactivex.create>`
     - Create an Observable from scratch by calling observer methods programmatically.
   * - :func:`empty <reactivex.empty>`
     - Creates an Observable that emits no item and completes immediately.
   * - :func:`from_ <reactivex.from_>`
     - Convert some other object or data structure into an Observable.
   * - :func:`interval <reactivex.interval>`
     - Create an Observable that emits a sequence of integers spaced by a particular time interval.
   * - :func:`just <reactivex.just>`
     - Convert an object or a set of objects into an Observable that emits that object or those objects.
   * - :func:`never <reactivex.never>`
     - Creates an Observable that never completes.
   * - :func:`range <reactivex.range>`
     - Create an Observable that emits a range of sequential integers.
   * - :func:`repeat_value <reactivex.repeat_value>`
     - Create an Observable that emits a particular item or sequence of items repeatedly.
   * - :func:`start <reactivex.start>`
     - Create an Observable that emits the return value of a function.
   * - :func:`throw <reactivex.throw>`
     - Creates an Observable that terminates with an error.
   * - :func:`timer <reactivex.timer>`
     - Create an Observable that emits a single item after a given delay.

Transforming Observables
------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`as_observable <reactivex.operators.as_observable>`
     - Hide the identity of an Observable.
   * - :func:`buffer <reactivex.operators.buffer>`
     - Periodically gather items from an Observable into bundles and emit these bundles rather than emitting the items one at a time.
   * - :func:`buffer_toggle <reactivex.operators.buffer_toggle>`
     - Collect overlapping buffers opened and closed by Observables.
   * - :func:`buffer_when <reactivex.operators.buffer_when>`
     - Collect successive buffers using an Observable to close each one.
   * - :func:`buffer_with_count <reactivex.operators.buffer_with_count>`
     - Collect items into buffers based on item counts.
   * - :func:`buffer_with_time <reactivex.operators.buffer_with_time>`
     - Collect items into buffers based on time intervals.
   * - :func:`buffer_with_time_or_count <reactivex.operators.buffer_with_time_or_count>`
     - Close a buffer when its time or item count limit is reached.
   * - :func:`concat_map <reactivex.operators.concat_map>`
     - Map each source value to an Observable and emit each inner sequence in order, waiting for one to complete before subscribing to the next.
   * - :func:`expand <reactivex.operators.expand>`
     - Recursively project emitted items into more Observables.
   * - :func:`flat_map <reactivex.operators.flat_map>`
     - Transform the items emitted by an Observable into Observables, then flatten the emissions from those into a single Observable.
   * - :func:`flat_map_indexed <reactivex.operators.flat_map_indexed>`
     - Map each item and its index to an Observable, then merge the results.
   * - :func:`flat_map_latest <reactivex.operators.flat_map_latest>`
     - Map each item to an Observable and emit from the most recent one.
   * - :func:`group_by <reactivex.operators.group_by>`
     - Divide an Observable into a set of Observables that each emit a different group of items from the original Observable, organized by key.
   * - :func:`group_by_until <reactivex.operators.group_by_until>`
     - Group items by key and close each group using a duration Observable.
   * - :func:`map <reactivex.operators.map>`
     - Transform the items emitted by an Observable by applying a function to each item.
   * - :func:`map_indexed <reactivex.operators.map_indexed>`
     - Transform each item using its value and index.
   * - :func:`pairwise <reactivex.operators.pairwise>`
     - Emit consecutive items as pairs.
   * - :func:`pluck <reactivex.operators.pluck>`
     - Extract a key from each dictionary-like item.
   * - :func:`pluck_attr <reactivex.operators.pluck_attr>`
     - Extract an attribute from each item.
   * - :func:`scan <reactivex.operators.scan>`
     - Apply a function to each item emitted by an Observable, sequentially, and emit each successive value.
   * - :func:`slice <reactivex.operators.slice>`
     - Select a slice of the source sequence.
   * - :func:`starmap <reactivex.operators.starmap>`
     - Transform tuple items by unpacking them into a function.
   * - :func:`starmap_indexed <reactivex.operators.starmap_indexed>`
     - Transform indexed tuple items by unpacking their values and index.
   * - :func:`switch_map <reactivex.operators.switch_map>`
     - Projects each source value to an Observable which is merged in the output Observable, emitting values only from the most recently projected Observable.
   * - :func:`switch_map_indexed <reactivex.operators.switch_map_indexed>`
     - Map each item and its index to an Observable, switching to the latest one.
   * - :func:`window <reactivex.operators.window>`
     - Periodically subdivide items from an Observable into Observable windows and emit these windows rather than emitting the items one at a time.
   * - :func:`window_toggle <reactivex.operators.window_toggle>`
     - Create overlapping windows opened and closed by Observables.
   * - :func:`window_when <reactivex.operators.window_when>`
     - Create successive windows using an Observable to close each one.
   * - :func:`window_with_count <reactivex.operators.window_with_count>`
     - Create windows based on item counts.
   * - :func:`window_with_time <reactivex.operators.window_with_time>`
     - Create windows based on time intervals.
   * - :func:`window_with_time_or_count <reactivex.operators.window_with_time_or_count>`
     - Close a window when its time or item count limit is reached.

Filtering Observables
----------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`debounce <reactivex.operators.debounce>`
     - Only emit an item from an Observable if a particular timespan has passed without it emitting another item.
   * - :func:`distinct <reactivex.operators.distinct>`
     - Suppress duplicate items emitted by an Observable.
   * - :func:`distinct_until_changed <reactivex.operators.distinct_until_changed>`
     - Suppress consecutive duplicate items.
   * - :func:`element_at <reactivex.operators.element_at>`
     - Emit only item n emitted by an Observable.
   * - :func:`element_at_or_default <reactivex.operators.element_at_or_default>`
     - Emit the item at an index, or a default if it is absent.
   * - :func:`filter <reactivex.operators.filter>`
     - Emit only those items from an Observable that pass a predicate test.
   * - :func:`filter_indexed <reactivex.operators.filter_indexed>`
     - Keep items matching a predicate that receives the item and index.
   * - :func:`find <reactivex.operators.find>`
     - Emit the first item matching a predicate.
   * - :func:`find_index <reactivex.operators.find_index>`
     - Emit the index of the first item matching a predicate.
   * - :func:`first <reactivex.operators.first>`
     - Emit only the first item, or the first item that meets a condition, from an Observable.
   * - :func:`first_or_default <reactivex.operators.first_or_default>`
     - Emit the first matching item, or a default if none matches.
   * - :func:`ignore_elements <reactivex.operators.ignore_elements>`
     - Do not emit any items from an Observable but mirror its termination notification.
   * - :func:`is_empty <reactivex.operators.is_empty>`
     - Emit whether the source has no items.
   * - :func:`last <reactivex.operators.last>`
     - Emit only the last item emitted by an Observable.
   * - :func:`last_or_default <reactivex.operators.last_or_default>`
     - Emit the last matching item, or a default if none matches.
   * - :func:`sample <reactivex.operators.sample>`
     - Emit the most recent item emitted by an Observable within periodic time intervals.
   * - :func:`single <reactivex.operators.single>`
     - Emit the only matching item, or signal an error if there is not exactly one.
   * - :func:`single_or_default <reactivex.operators.single_or_default>`
     - Emit the only matching item, or a default if none matches.
   * - :func:`single_or_default_async <reactivex.operators.single_or_default_async>`
     - Emit the only source item, or an optional default if empty.
   * - :func:`skip <reactivex.operators.skip>`
     - Suppress the first n items emitted by an Observable.
   * - :func:`skip_last <reactivex.operators.skip_last>`
     - Suppress the last n items emitted by an Observable.
   * - :func:`skip_last_with_time <reactivex.operators.skip_last_with_time>`
     - Skip items from the final time interval of the source.
   * - :func:`skip_until_with_time <reactivex.operators.skip_until_with_time>`
     - Skip items until a specified time.
   * - :func:`skip_while_indexed <reactivex.operators.skip_while_indexed>`
     - Skip items while an indexed predicate holds.
   * - :func:`skip_with_time <reactivex.operators.skip_with_time>`
     - Skip items for a duration from subscription.
   * - :func:`take <reactivex.operators.take>`
     - Emit only the first n items emitted by an Observable.
   * - :func:`take_last <reactivex.operators.take_last>`
     - Emit only the last n items emitted by an Observable.
   * - :func:`take_last_buffer <reactivex.operators.take_last_buffer>`
     - Collect and emit the final items as a list when the source completes.
   * - :func:`take_last_with_time <reactivex.operators.take_last_with_time>`
     - Emit items from the final time interval of the source.
   * - :func:`take_until_with_time <reactivex.operators.take_until_with_time>`
     - Emit items until a specified time.
   * - :func:`take_while_indexed <reactivex.operators.take_while_indexed>`
     - Emit items while an indexed predicate holds.
   * - :func:`take_with_time <reactivex.operators.take_with_time>`
     - Emit items for a duration from subscription.

Combining Observables
----------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`combine_latest <reactivex.operators.combine_latest>`
     - When an item is emitted by either of two Observables, combine the latest item emitted by each Observable via a specified function and emit items based on the results of this function.
   * - :func:`concat_all <reactivex.operators.concat_all>`
     - Flatten an Observable of Observables in source order, waiting for each inner sequence to complete before subscribing to the next.
   * - :func:`exclusive <reactivex.operators.exclusive>`
     - Flatten one inner Observable at a time, dropping others while one is active.
   * - :func:`fork_join <reactivex.operators.fork_join>`
     - Wait for Observables to complete and then combine last values they emitted into a tuple.
   * - :func:`group_join <reactivex.operators.group_join>`
     - Join items from two Observables while their windows overlap.
   * - :func:`join <reactivex.operators.join>`
     - Combine items emitted by two Observables whenever an item from one Observable is emitted during a time window defined according to an item emitted by the other Observable.
   * - :func:`merge <reactivex.operators.merge>`
     - Combine multiple Observables into one by merging their emissions.
   * - :func:`merge_all <reactivex.operators.merge_all>`
     - Flatten an Observable of Observables by subscribing to inner sequences as they arrive.
   * - :func:`partition <reactivex.operators.partition>`
     - Split the source into matching and nonmatching Observables.
   * - :func:`partition_indexed <reactivex.operators.partition_indexed>`
     - Split the source using a predicate that receives the item and index.
   * - :func:`start_with <reactivex.operators.start_with>`
     - Emit a specified sequence of items before beginning to emit the items from the source Observable.
   * - :func:`switch_latest <reactivex.operators.switch_latest>`
     - Convert an Observable that emits Observables into a single Observable that emits the items emitted by the most-recently-emitted of those Observables.
   * - :func:`with_latest_from <reactivex.operators.with_latest_from>`
     - Combine each source item with the latest values from other Observables.
   * - :func:`zip <reactivex.operators.zip>`
     - Combine the emissions of multiple Observables together via a specified function and emit single items for each combination based on the results of this function.
   * - :func:`zip_with_iterable <reactivex.operators.zip_with_iterable>`
     - Pair source items with items from an iterable.
   * - :func:`zip_with_list <reactivex.operators.zip_with_list>`
     - Alias for zip_with_iterable.

Working with Time
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`debounce <reactivex.operators.debounce>`
     - Emit an item only after no newer item arrives during a specified period.
   * - :func:`delay <reactivex.operators.delay>`
     - Shift source items and completion forward by a fixed duration.
   * - :func:`delay_subscription <reactivex.operators.delay_subscription>`
     - Wait before subscribing to the source Observable.
   * - :func:`delay_with_mapper <reactivex.operators.delay_with_mapper>`
     - Delay each item using an Observable selected by a mapper; optionally delay subscription too.
   * - :func:`sample <reactivex.operators.sample>`
     - Emit the latest source item at sampling times.
   * - :func:`throttle_first <reactivex.operators.throttle_first>`
     - Emit the first item in each time window.
   * - :func:`time_interval <reactivex.operators.time_interval>`
     - Measure the time between source items.
   * - :func:`timeout <reactivex.operators.timeout>`
     - Signal an error or switch to another Observable when an item takes too long.
   * - :func:`timestamp <reactivex.operators.timestamp>`
     - Attach a timestamp to each source item.

Error Handling
---------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`catch <reactivex.operators.catch>`
     - Continues observable sequences which are terminated with an exception by switching over to the next observable sequence.
   * - :func:`on_error_resume_next <reactivex.operators.on_error_resume_next>`
     - Continue with another Observable after completion or an error.
   * - :func:`retry <reactivex.operators.retry>`
     - If a source Observable sends an onError notification, resubscribe to it in the hopes that it will complete without error.

Utility Operators
------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`delay <reactivex.operators.delay>`
     - Shift the emissions from an Observable forward in time by a particular amount.
   * - :func:`delay_subscription <reactivex.operators.delay_subscription>`
     - Delay subscribing to the source Observable.
   * - :func:`delay_with_mapper <reactivex.operators.delay_with_mapper>`
     - Delay items according to Observables produced by a mapper.
   * - :func:`dematerialize <reactivex.operators.dematerialize>`
     - Dematerializes the explicit notification values of an observable sequence as implicit notifications.
   * - :func:`do <reactivex.operators.do>`
     - Register an action to take upon a variety of Observable lifecycle events.
   * - :func:`do_action <reactivex.operators.do_action>`
     - Run actions for source notifications without changing them.
   * - :func:`finally_action <reactivex.operators.finally_action>`
     - Run an action when the subscription terminates or is disposed.
   * - :func:`materialize <reactivex.operators.materialize>`
     - Materializes the implicit notifications of an observable sequence as explicit notification values.
   * - :func:`observe_on <reactivex.operators.observe_on>`
     - Specify the scheduler on which an observer will observe this Observable.
   * - :meth:`subscribe <reactivex.Observable.subscribe>`
     - Operate upon the emissions and notifications from an Observable.
   * - :func:`subscribe_on <reactivex.operators.subscribe_on>`
     - Specify the scheduler an Observable should use when it is subscribed to.
   * - :func:`tap <reactivex.operators.tap>`
     - Alias for do_action.
   * - :func:`throttle_first <reactivex.operators.throttle_first>`
     - Emit the first item in each time window.
   * - :func:`throttle_with_mapper <reactivex.operators.throttle_with_mapper>`
     - Suppress items followed by another item before a mapped duration ends.
   * - :func:`throttle_with_timeout <reactivex.operators.throttle_with_timeout>`
     - Alias for debounce.
   * - :func:`time_interval <reactivex.operators.time_interval>`
     - Convert an Observable that emits items into one that emits indications of the amount of time elapsed between those emissions.
   * - :func:`timeout <reactivex.operators.timeout>`
     - Mirror the source Observable, but issue an error notification if a particular period of time elapses without any emitted items.
   * - :func:`timeout_with_mapper <reactivex.operators.timeout_with_mapper>`
     - Switch to another Observable when a mapped timeout expires.
   * - :func:`timestamp <reactivex.operators.timestamp>`
     - Attach a timestamp to each item emitted by an Observable.
   * - :func:`to_dict <reactivex.operators.to_dict>`
     - Collect source items into a dictionary.
   * - :func:`to_future <reactivex.operators.to_future>`
     - Convert the final source item into a Future.
   * - :func:`to_iterable <reactivex.operators.to_iterable>`
     - Collect source items into a list emitted on completion.
   * - :func:`to_list <reactivex.operators.to_list>`
     - Collect source items into a list emitted on completion.
   * - :func:`to_marbles <reactivex.operators.to_marbles>`
     - Render source notifications as a marble diagram string.
   * - :func:`to_set <reactivex.operators.to_set>`
     - Collect source items into a set emitted on completion.

Conditional and Boolean Operators
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`all <reactivex.operators.all>`
     - Determine whether all items emitted by an Observable meet some criteria.
   * - :func:`amb <reactivex.operators.amb>`
     - Given two or more source Observables, emit all of the items from only the first of these Observables to emit an item.
   * - :func:`contains <reactivex.operators.contains>`
     - Determine whether an Observable emits a particular item or not.
   * - :func:`default_if_empty <reactivex.operators.default_if_empty>`
     - Emit items from the source Observable, or a default item if the source Observable emits nothing.
   * - :func:`do_while <reactivex.operators.do_while>`
     - Repeat the source at least once, then while a condition holds.
   * - :func:`repeat <reactivex.operators.repeat>`
     - Repeat the source a specified number of times or indefinitely.
   * - :func:`sequence_equal <reactivex.operators.sequence_equal>`
     - Determine whether two Observables emit the same sequence of items.
   * - :func:`skip_until <reactivex.operators.skip_until>`
     - Discard items emitted by an Observable until a second Observable emits an item.
   * - :func:`skip_while <reactivex.operators.skip_while>`
     - Discard items emitted by an Observable until a specified condition becomes false.
   * - :func:`some <reactivex.operators.some>`
     - Emit whether any item matches a predicate.
   * - :func:`take_until <reactivex.operators.take_until>`
     - Discard items emitted by an Observable after a second Observable emits an item or terminates.
   * - :func:`take_while <reactivex.operators.take_while>`
     - Discard items emitted by an Observable after a specified condition becomes false.
   * - :func:`while_do <reactivex.operators.while_do>`
     - Repeat the source while a condition holds.

Mathematical and Aggregate Operators
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :func:`average <reactivex.operators.average>`
     - Calculates the average of numbers emitted by an Observable and emits this average.
   * - :func:`concat <reactivex.operators.concat>`
     - Emit the emissions from two or more Observables without interleaving them.
   * - :func:`count <reactivex.operators.count>`
     - Count the number of items emitted by the source Observable and emit only this value.
   * - :func:`max <reactivex.operators.max>`
     - Determine, and emit, the maximum-valued item emitted by an Observable.
   * - :func:`max_by <reactivex.operators.max_by>`
     - Emit the items with the maximum mapped key.
   * - :func:`min <reactivex.operators.min>`
     - Determine, and emit, the minimum-valued item emitted by an Observable.
   * - :func:`min_by <reactivex.operators.min_by>`
     - Emit the items with the minimum mapped key.
   * - :func:`reduce <reactivex.operators.reduce>`
     - Apply a function to each item emitted by an Observable, sequentially, and emit the final value.
   * - :func:`sum <reactivex.operators.sum>`
     - Calculate the sum of numbers emitted by an Observable and emit this sum.

Connectable Observable Operators
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Operator
     - Description
   * - :meth:`connect <reactivex.ConnectableObservable.connect>`
     - Instruct a connectable Observable to begin emitting items to its subscribers.
   * - :func:`multicast <reactivex.operators.multicast>`
     - Share a source through a Subject or Subject factory.
   * - :func:`publish <reactivex.operators.publish>`
     - Convert an ordinary Observable into a connectable Observable.
   * - :func:`publish_value <reactivex.operators.publish_value>`
     - Share a source and provide an initial value to new subscribers.
   * - :func:`ref_count <reactivex.operators.ref_count>`
     - Make a Connectable Observable behave like an ordinary Observable.
   * - :func:`replay <reactivex.operators.replay>`
     - Ensure that all observers see the same sequence of emitted items, even if they subscribe after the Observable has begun emitting items.
   * - :func:`share <reactivex.operators.share>`
     - Share a single source subscription among subscribers.
