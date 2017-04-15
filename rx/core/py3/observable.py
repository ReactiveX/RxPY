from abc import ABCMeta, abstractmethod


class Observable(metaclass=ABCMeta):
    @abstractmethod
    def subscribe(self, observer):
        return NotImplemented


    def aggregate(self, accumulator, seed):
        """
        Applies an accumulator function over an observable sequence,
        returning the result of the aggregation as a single element in the
        result sequence. The specified seed value is used as the initial
        accumulator value.
    
        For aggregation behavior with incremental intermediate results, see
        Observable.scan.
    
        Example:
        1 - res = source.reduce(lambda acc, x: acc + x)
        2 - res = source.reduce(lambda acc, x: acc + x, 0)
    
        Keyword arguments:
        :param types.FunctionType accumulator: An accumulator function to be
            invoked on each element.
        :param T seed: Optional initial accumulator value.
    
        :returns: An observable sequence containing a single element with the
            final accumulator value.
        :rtype: Observable
        """
        pass

    def all(self, predicate):
        """
        Determines whether all elements of an observable sequence satisfy a
        condition.
    
        1 - res = source.all(lambda value: value.length > 3)
    
        Keyword arguments:
        :param bool predicate: A function to test each element for a condition.
    
        :returns: An observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
        """
        pass

    @classmethod
    def amb(cls, *args, acc, items, func, item):
        """
        Propagates the observable sequence that reacts first.
    
        E.g. winner = rx.Observable.amb(xs, ys, zs)
    
        Returns an observable sequence that surfaces any of the given sequences,
        whichever reacted first.
        """
        pass

    def and_(self, right):
        """
        Creates a pattern that matches when both observable sequences
        have an available value.
    
        :param Observable right: Observable sequence to match with the
            current sequence.
        :returns: Pattern object that matches when both observable sequences
            have an available value.
        """
        pass

    def as_observable(self):
        """
        Hides the identity of an observable sequence.
    
        :returns: An observable sequence that hides the identity of the source
            sequence.
        :rtype: Observable
        """
        pass

    def average(self, key_selector, accumulator, mapper, seed):
        """
        Computes the average of an observable sequence of values that are in
        the sequence or obtained by invoking a transform function on each
        element of the input sequence if present.
    
        Example
        res = source.average();
        res = source.average(lambda x: x.value)
    
        :param Observable self: Observable to average.
        :param types.FunctionType key_selector: A transform function to apply to
            each element.
    
        :returns: An observable sequence containing a single element with the
            average of the sequence of values.
        :rtype: Observable
        """
        pass

    def buffer(self, buffer_openings, buffer_closing_selector=None):
        """
        Projects each element of an observable sequence into zero or more
        buffers.
    
        Keyword arguments:
        buffer_openings -- Observable sequence whose elements denote the
            creation of windows.
        buffer_closing_selector -- [optional] A function invoked to define the
            closing of each produced window. If a closing selector function is
            specified for the first parameter, this parameter is ignored.
    
        Returns an observable sequence of windows.
        """
        pass

    def buffer_with_count(self, count, skip=None):
        """
        Projects each element of an observable sequence into zero or more
        buffers which are produced based on element count information.
    
        Example:
        res = xs.buffer_with_count(10)
        res = xs.buffer_with_count(10, 1)
    
        Keyword parameters:
        count -- {Number} Length of each buffer.
        skip -- {Number} [Optional] Number of elements to skip between creation
            of consecutive buffers. If not provided, defaults to the count.
    
        Returns an observable {Observable} sequence of buffers.
        """
        pass

    def buffer_with_time(self, timespan, timeshift=None, scheduler=None):
        """
        Projects each element of an observable sequence into zero or more
        buffers which are produced based on timing information.
    
        # non-overlapping segments of 1 second
        1 - res = xs.buffer_with_time(1000)
        # segments of 1 second with time shift 0.5 seconds
        2 - res = xs.buffer_with_time(1000, 500)
    
        Keyword arguments:
        timespan -- Length of each buffer (specified as an integer denoting
            milliseconds).
        timeshift -- [Optional] Interval between creation of consecutive
            buffers (specified as an integer denoting milliseconds), or an
            optional scheduler parameter. If not specified, the time shift
            corresponds to the timespan parameter, resulting in non-overlapping
            adjacent buffers.
        scheduler -- [Optional] Scheduler to run buffer timers on. If not
            specified, the timeout scheduler is used.
    
        Returns an observable sequence of buffers.
        """
        pass

    def buffer_with_time_or_count(self, timespan, count, scheduler=None):
        """
        Projects each element of an observable sequence into a buffer that
        is completed when either it's full or a given amount of time has
        elapsed.
    
        # 5s or 50 items in an array
        1 - res = source.buffer_with_time_or_count(5000, 50)
        # 5s or 50 items in an array
        2 - res = source.buffer_with_time_or_count(5000, 50, Scheduler.timeout)
    
        Keyword arguments:
        timespan -- Maximum time length of a buffer.
        count -- Maximum element count of a buffer.
        scheduler -- [Optional] Scheduler to run bufferin timers on. If not
            specified, the timeout scheduler is used.
    
        Returns an observable sequence of buffers.
        """
        pass

    @classmethod
    def case(cls, selector, sources, default_source, scheduler=None):
        """
        Uses selector to determine which source in sources to use.
        There is an alias 'switch_case'.
    
        Example:
        1 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 })
        2 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 }, obs0)
        3 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 },
                                     scheduler=scheduler)
    
        Keyword arguments:
        :param types.FunctionType selector: The function which extracts the value
            for to test in a case statement.
        :param list sources: A object which has keys which correspond to the case
            statement labels.
        :param Observable default_source: The observable sequence or Promise that
            will be run if the sources are not matched. If this is not provided, it
            defaults to rx.Observabe.empty with the specified scheduler.
    
        :returns: An observable sequence which is determined by a case statement.
        :rtype: Observable
        """
        pass

    @classmethod
    def catch_exception(cls, *args):
        """
        Continues an observable sequence that is terminated by an
        exception with the next observable sequence.
    
        1 - res = Observable.catch_exception(xs, ys, zs)
        2 - res = Observable.catch_exception([xs, ys, zs])
    
        Returns an observable sequence containing elements from consecutive
        source sequences until a source sequence terminates successfully.
        """
        pass

    @classmethod
    def combine_latest(cls, *args):
        """
        Merges the specified observable sequences into one observable
        sequence by using the selector function whenever any of the
        observable sequences produces an element.
    
        1 - obs = Observable.combine_latest(obs1, obs2, obs3,
                                           lambda o1, o2, o3: o1 + o2 + o3)
        2 - obs = Observable.combine_latest([obs1, obs2, obs3],
                                            lambda o1, o2, o3: o1 + o2 + o3)
    
        Returns an observable sequence containing the result of combining
        elements of the sources using the specified result selector
        function.
        """
        pass

    @classmethod
    def concat(cls, *args):
        """
        Concatenates all the observable sequences.
    
        1 - res = Observable.concat(xs, ys, zs)
        2 - res = Observable.concat([xs, ys, zs])
    
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        pass

    def concat_all(self):
        """
        Concatenates an observable sequence of observable sequences.
    
        Returns an observable sequence that contains the elements of each
        observed inner sequence, in sequential order.
        """
        pass

    def contains(self, value, comparer=None):
        """
        Determines whether an observable sequence contains a specified
        element with an optional equality comparer.
    
        Example
        1 - res = source.contains(42)
        2 - res = source.contains({ "value": 42 }, lambda x, y: x["value"] == y["value")
    
        Keyword parameters:
        value -- The value to locate in the source sequence.
        comparer -- {Function} [Optional] An equality comparer to compare elements.
    
        Returns an observable {Observable} sequence containing a single element
        determining whether the source sequence contains an element that has
        the specified value.
        """
        pass

    def controlled(self, enable_queue, scheduler=None):
        """
        Attach a controller to the observable sequence
    
        Attach a controller to the observable sequence with the ability to
        queue.
    
        Example:
        source = rx.Observable.interval(100).controlled()
        source.request(3) # Reads 3 values
    
        Keyword arguments:
        :param bool enable_queue: truthy value to determine if values should
            be queued pending the next request
        :param Scheduler scheduler: determines how the requests will be scheduled
        :returns: The observable sequence which only propagates values on request.
        :rtype: Observable
        """
        pass

    def count(self, predicate):
        """
        Returns an observable sequence containing a value that represents
        how many elements in the specified observable sequence satisfy a
        condition if provided, else the count of items.
    
        1 - res = source.count()
        2 - res = source.count(lambda x: x > 3)
    
        Keyword arguments:
        :param types.FunctionType predicate: A function to test each element for a
            condition.
    
        :returns: An observable sequence containing a single element with a
        number that represents how many elements in the input sequence satisfy
        the condition in the predicate function if provided, else the count of
        items in the sequence.
        :rtype: Observable
        """
        pass

    @classmethod
    def create(cls):
        pass

    @classmethod
    def create_with_disposable(cls):
        pass

    def debounce(self, duetime, scheduler=None):
        """
        Ignores values from an observable sequence which are followed by
        another value before duetime.
    
        Example:
        1 - res = source.debounce(5000) # 5 seconds
        2 - res = source.debounce(5000, scheduler)
    
        Keyword arguments:
        duetime -- {Number} Duration of the throttle period for each value
            (specified as an integer denoting milliseconds).
        scheduler -- {Scheduler} [Optional]  Scheduler to run the throttle
            timers on. If not specified, the timeout scheduler is used.
    
        Returns {Observable} The debounced sequence.
        """
        pass

    def default_if_empty(self, default_value):
        """
        Returns the elements of the specified sequence or the specified value
        in a singleton sequence if the sequence is empty.
    
        res = obs = xs.defaultIfEmpty()
        obs = xs.defaultIfEmpty(False
    
        Keyword arguments:
        default_value -- The value to return if the sequence is empty. If not
            provided, this defaults to None.
    
        Returns an observable {Observable} sequence that contains the specified
        default value if the source is empty otherwise, the elements of the
        source itself.
        """
        pass

    @classmethod
    def defer(cls, observable_factory):
        """
        Returns an observable sequence that invokes the specified factory
        function whenever a new observer subscribes.
    
        Example:
        1 - res = rx.Observable.defer(lambda: rx.Observable.from_([1,2,3]))
    
        Keyword arguments:
        :param types.FunctionType observable_factory: Observable factory function
            to invoke for each observer that subscribes to the resulting sequence.
    
        :returns: An observable sequence whose observers trigger an invocation
        of the given observable factory function.
        :rtype: Observable
        """
        pass

    def delay(self, duetime, scheduler=None):
        """
        Time shifts the observable sequence by duetime. The relative time
        intervals between the values are preserved.
    
        1 - res = rx.Observable.delay(datetime())
        2 - res = rx.Observable.delay(datetime(), Scheduler.timeout)
    
        3 - res = rx.Observable.delay(5000)
        4 - res = rx.Observable.delay(5000, Scheduler.timeout)
    
        Keyword arguments:
        :param datetime|int duetime: Absolute (specified as a datetime object) or
            relative time (specified as an integer denoting milliseconds) by which
            to shift the observable sequence.
        :param Scheduler scheduler: [Optional] Scheduler to run the delay timers on.
            If not specified, the timeout scheduler is used.
    
        :returns: Time-shifted sequence.
        :rtype: Observable
        """
        pass

    def delay_subscription(self, duetime, scheduler=None):
        """
        Time shifts the observable sequence by delaying the subscription.
    
        1 - res = source.delay_subscription(5000) # 5s
        2 - res = source.delay_subscription(5000, Scheduler.timeout) # 5 seconds
    
        duetime -- Absolute or relative time to perform the subscription at.
        scheduler [Optional] Scheduler to run the subscription delay timer on.
            If not specified, the timeout scheduler is used.
    
        Returns time-shifted sequence.
        """
        pass

    def delay_with_selector(self, subscription_delay=None, delay_duration_selector=None):
        """
        Time shifts the observable sequence based on a subscription delay
        and a delay selector function for each element.
    
        # with selector only
        1 - res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
        # with delay and selector
        2 - res = source.delay_with_selector(Observable.timer(2000),
                                             lambda x: Observable.timer(x))
    
        subscription_delay -- [Optional] Sequence indicating the delay for the
            subscription to the source.
        delay_duration_selector [Optional] Selector function to retrieve a
            sequence indicating the delay for each given element.
    
        Returns time-shifted sequence.
        """
        pass

    def dematerialize(self):
        """
        Dematerializes the explicit notification values of an observable
        sequence as implicit notifications.
    
        Returns an observable sequence exhibiting the behavior corresponding to
        the source sequence's notification values.
        """
        pass

    def distinct(self, key_selector=None, comparer=None):
        """
        Returns an observable sequence that contains only distinct elements
        according to the key_selector and the comparer. Usage of this operator
        should be considered carefully due to the maintenance of an internal
        lookup structure which can grow large.
    
        Example:
        res = obs = xs.distinct()
        obs = xs.distinct(lambda x: x.id)
        obs = xs.distinct(lambda x: x.id, lambda a,b: a == b)
    
        Keyword arguments:
        key_selector -- {Function} [Optional]  A function to compute the
            comparison key for each element.
        comparer -- {Function} [Optional]  Used to compare items in the
            collection.
    
        Returns an observable {Observable} sequence only containing the distinct
        elements, based on a computed key value, from the source sequence.
        """
        pass

    def distinct_until_changed(self, key_selector=None, comparer=None):
        """
        Returns an observable sequence that contains only distinct
        contiguous elements according to the key_selector and the comparer.
    
        1 - obs = observable.distinct_until_changed();
        2 - obs = observable.distinct_until_changed(lambda x: x.id)
        3 - obs = observable.distinct_until_changed(lambda x: x.id,
                                                    lambda x, y: x == y)
    
        key_selector -- [Optional] A function to compute the comparison key for
            each element. If not provided, it projects the value.
        comparer -- [Optional] Equality comparer for computed key values. If
            not provided, defaults to an equality comparer function.
    
        Return An observable sequence only containing the distinct contiguous
        elements, based on a computed key value, from the source sequence.
        """
        pass

    def do_action(self, on_next=None, on_error=None, on_completed=None, observer=None):
        """
        Invokes an action for each element in the observable sequence and
        invokes an action on graceful or exceptional termination of the
        observable sequence. This method can be used for debugging, logging,
        etc. of query behavior by intercepting the message stream to run
        arbitrary actions for messages on the pipeline.
    
        1 - observable.do_action(observer)
        2 - observable.do_action(on_next)
        3 - observable.do_action(on_next, on_error)
        4 - observable.do_action(on_next, on_error, on_completed)
    
        observer -- [Optional] Observer, or ...
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke on exceptional termination
            of the observable sequence.
        on_completed -- [Optional] Action to invoke on graceful termination
            of the observable sequence.
    
        Returns the source sequence with the side-effecting behavior applied.
        """
        pass

    def do_after_next(self, after_next):
        """
        Invokes an action with each element after it has been emitted downstream.
        This can be helpful for debugging, logging, and other side effects.
    
        after_next -- Action to invoke on each element after it has been emitted
        """
        pass

    def do_after_terminate(self, after_terminate):
        """
        Invokes an action after an on_complete() or on_error() event.
         This can be helpful for debugging, logging, and other side effects when completion or an error terminates an operation
    
    
        on_terminate -- Action to invoke after on_complete or on_error is called
        """
        pass

    def do_finally(self, finally_action):
        """
        Invokes an action after an on_complete(), on_error(), or disposal event occurs
         This can be helpful for debugging, logging, and other side effects when completion, an error, or disposal terminates an operation.
        Note this operator will strive to execute the finally_action once, and prevent any redudant calls
    
        finally_action -- Action to invoke after on_complete, on_error, or disposal is called
        """
        pass

    def do_on_dispose(self, on_dispose):
        """
        Invokes an action on disposal.
         This can be helpful for debugging, logging, and other side effects on the disposal of an operation.
    
    
        on_dispose -- Action to invoke on disposal
        """
        pass

    def do_on_subscribe(self, on_subscribe):
        """
        Invokes an action on subscription.
        This can be helpful for debugging, logging, and other side effects on the start of an operation.
    
        on_subscribe -- Action to invoke on subscription
        """
        pass

    def do_on_terminate(self, on_terminate):
        """
        Invokes an action on an on_complete() or on_error() event.
         This can be helpful for debugging, logging, and other side effects when completion or an error terminates an operation.
    
    
        on_terminate -- Action to invoke when on_complete or on_error is called
        """
        pass

    def do_while(self, condition):
        """
        Repeats source as long as condition holds emulating a do while loop.
    
        Keyword arguments:
        condition -- {Function} The condition which determines if the source
            will be repeated.
    
        Returns an observable {Observable} sequence which is repeated as long
        as the condition holds.
        """
        pass

    def element_at(self, index):
        """
        Returns the element at a specified index in a sequence.
    
        Example:
        res = source.element_at(5)
    
        Keyword arguments:
        :param int index: The zero-based index of the element to retrieve.
    
        :returns: An observable  sequence that produces the element at the
        specified position in the source sequence.
        :rtype: Observable
        """
        pass

    def element_at_or_default(self, index, default_value=None):
        """
        Returns the element at a specified index in a sequence or a default
        value if the index is out of range.
    
        Example:
        res = source.element_at_or_default(5)
        res = source.element_at_or_default(5, 0)
    
        Keyword arguments:
        index -- {Number} The zero-based index of the element to retrieve.
        default_value -- [Optional] The default value if the index is outside
            the bounds of the source sequence.
    
        Returns an observable {Observable} sequence that produces the element at
            the specified position in the source sequence, or a default value if
            the index is outside the bounds of the source sequence.
        """
        pass

    @classmethod
    def empty(cls, scheduler=None):
        """
        Returns an empty observable sequence, using the specified scheduler
        to send out the single OnCompleted message.
    
        1 - res = rx.Observable.empty()
        2 - res = rx.Observable.empty(rx.Scheduler.timeout)
    
        scheduler -- Scheduler to send the termination call on.
    
        Returns an observable sequence with no elements.
        """
        pass

    def every(self, predicate):
        """
        Determines whether all elements of an observable sequence satisfy a
        condition.
    
        1 - res = source.all(lambda value: value.length > 3)
    
        Keyword arguments:
        :param bool predicate: A function to test each element for a condition.
    
        :returns: An observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
        """
        pass

    def exclusive(self):
        """
        Performs a exclusive waiting for the first to finish before
        subscribing to another observable. Observables that come in between
        subscriptions will be dropped on the floor.
    
        Returns an exclusive observable {Observable} with only the results that
        happen when subscribed.
        """
        pass

    def expand(self, selector, scheduler=None):
        """
        Expands an observable sequence by recursively invoking selector.
    
        selector -- {Function} Selector function to invoke for each produced
            element, resulting in another sequence to which the selector will be
            invoked recursively again.
        scheduler -- {Scheduler} [Optional] Scheduler on which to perform the
            expansion. If not provided, this defaults to the current thread
            scheduler.
    
        Returns an observable {Observable} sequence containing all the elements
        produced by the recursive expansion.
        """
        pass

    def filter(self, predicate):
        """
        Filters the elements of an observable sequence based on a predicate
        by incorporating the element's index.
    
        1 - source.filter(lambda value: value < 10)
        2 - source.filter(lambda value, index: value < 10 or index < 10)
    
        Keyword arguments:
        :param Observable self: Observable sequence to filter.
        :param (T, <int>) -> bool predicate: A function to test each source element
            for a condition; the
            second parameter of the function represents the index of the source
            element.
    
        :returns: An observable sequence that contains elements from the input
        sequence that satisfy the condition.
        :rtype: Observable
        """
        pass

    def finally_action(self, action):
        """
        Invokes a specified action after the source observable sequence
        terminates gracefully or exceptionally.
    
        Example:
        res = observable.finally(lambda: print('sequence ended')
    
        Keyword arguments:
        action -- {Function} Action to invoke after the source observable
            sequence terminates.
        Returns {Observable} Source sequence with the action-invoking
        termination behavior applied.
        """
        pass

    def find(self, predicate):
        """
        Searches for an element that matches the conditions defined by the
        specified predicate, and returns the first occurrence within the entire
        Observable sequence.
    
        Keyword arguments:
        predicate -- {Function} The predicate that defines the conditions of the
            element to search for.
    
        Returns an Observable {Observable} sequence with the first element that
        matches the conditions defined by the specified predicate, if found
        otherwise, None.
        """
        pass

    def find_index(self, predicate):
        """
        Searches for an element that matches the conditions defined by the
        specified predicate, and returns an Observable sequence with the
        zero-based index of the first occurrence within the entire Observable
        sequence.
    
        Keyword Arguments:
        predicate -- {Function} The predicate that defines the conditions of the
            element to search for.
    
        Returns an observable {Observable} sequence with the zero-based index of
        the first occurrence of an element that matches the conditions defined
        by match, if found; otherwise, -1.
        """
        pass

    def first(self, predicate=None):
        """
        Returns the first element of an observable sequence that satisfies
        the condition in the predicate if present else the first item in the
        sequence.
    
        Example:
        res = res = source.first()
        res = res = source.first(lambda x: x > 3)
    
        Keyword arguments:
        predicate -- {Function} [Optional] A predicate function to evaluate for
            elements in the source sequence.
    
        Returns {Observable} Sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate if
        provided, else the first item in the sequence.
        """
        pass

    def first_or_default(self, predicate=None, default_value=None):
        """
        Returns the first element of an observable sequence that satisfies
        the condition in the predicate, or a default value if no such element
        exists.
    
        Example:
        res = source.first_or_default()
        res = source.first_or_default(lambda x: x > 3)
        res = source.first_or_default(lambda x: x > 3, 0)
        res = source.first_or_default(null, 0)
    
        Keyword arguments:
        predicate -- {Function} [optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- {Any} [Optional] The default value if no such element
            exists.  If not specified, defaults to None.
    
        Returns {Observable} Sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate, or a
        default value if no such element exists.
        """
        pass

    def flat_map(self, selector, result_selector=None):
        """
        One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.
    
        1 - source.select_many(lambda x: Observable.range(0, x))
    
        Or:
        Projects each element of an observable sequence to an observable
        sequence, invokes the result selector for the source element and each
        of the corresponding inner sequence's elements, and merges the results
        into one observable sequence.
    
        1 - source.select_many(lambda x: Observable.range(0, x), lambda x, y: x + y)
    
        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.
    
        1 - source.select_many(Observable.from_([1,2,3]))
    
        Keyword arguments:
        selector -- A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.
        result_selector -- [Optional] A transform function to apply to each
            element of the intermediate sequence.
    
        Returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence
        elements and their corresponding source element to a result element.
        """
        pass

    def flat_map_latest(self, selector):
        """
        Projects each element of an observable sequence into a new sequence
        of observable sequences by incorporating the element's index and then
        transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.
    
        Keyword arguments:
        selector -- {Function} A transform function to apply to each source
            element; the second parameter of the function represents the index
            of the source element.
    
        Returns an observable {Observable} sequence whose elements are the
        result of invoking the transform function on each element of source
        producing an Observable of Observable sequences and that at any point in
        time produces the elements of the most recent inner observable sequence
        that has been received.
        """
        pass

    @classmethod
    def for_in(cls, sources, result_selector):
        """
        Concatenates the observable sequences obtained by running the
        specified result selector for each element in source.
    
        sources -- {Array} An array of values to turn into an observable
            sequence.
        result_selector -- {Function} A function to apply to each item in the
            sources array to turn it into an observable sequence.
        Returns an observable {Observable} sequence from the concatenated
        observable sequences.
        """
        pass

    @classmethod
    def from_(cls, iterable, scheduler=None):
        """
        Converts an array to an observable sequence, using an optional
        scheduler to enumerate the array.
    
        1 - res = rx.Observable.from_iterable([1,2,3])
        2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)
    
        Keyword arguments:
        :param Observable cls: Observable class
        :param Scheduler scheduler: [Optional] Scheduler to run the
            enumeration of the input sequence on.
    
        :returns: The observable sequence whose elements are pulled from the
            given enumerable sequence.
        :rtype: Observable
        """
        pass

    @classmethod
    def from_callable(cls, supplier, scheduler=None):
        """
        Returns an observable sequence that contains a single element generate from a supplier,
           using the specified scheduler to send out observer messages.
    
           example
           res = rx.Observable.from_callable(lambda: calculate_value())
           res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error
    
           Keyword arguments:
           value -- Single element in the resulting observable sequence.
           scheduler -- [Optional] Scheduler to send the single element on. If
               not specified, defaults to Scheduler.immediate.
    
           Returns an observable sequence containing the single specified
           element derived from the supplier
           """
        pass

    @classmethod
    def from_callback(cls, func, selector=None):
        """
        Converts a callback function to an observable sequence.
    
        Keyword arguments:
        func -- {Function} Function with a callback as the last parameter to
            convert to an Observable sequence.
        selector -- {Function} [Optional] A selector which takes the arguments
            from the callback to produce a single item to yield on next.
    
        Returns {Function} A function, when executed with the required
        parameters minus the callback, produces an Observable sequence with a
        single value of the arguments to the callback as a list.
        """
        pass

    @classmethod
    def from_future(cls, future):
        """
        Converts a Future to an Observable sequence
    
        Keyword Arguments:
        future -- {Future} A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future
    
        Returns {Observable} An Observable sequence which wraps the existing
        future success and failure.
        """
        pass

    @classmethod
    def from_iterable(cls, iterable, scheduler=None):
        """
        Converts an array to an observable sequence, using an optional
        scheduler to enumerate the array.
    
        1 - res = rx.Observable.from_iterable([1,2,3])
        2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)
    
        Keyword arguments:
        :param Observable cls: Observable class
        :param Scheduler scheduler: [Optional] Scheduler to run the
            enumeration of the input sequence on.
    
        :returns: The observable sequence whose elements are pulled from the
            given enumerable sequence.
        :rtype: Observable
        """
        pass

    @classmethod
    def from_list(cls, iterable, scheduler=None):
        """
        Converts an array to an observable sequence, using an optional
        scheduler to enumerate the array.
    
        1 - res = rx.Observable.from_iterable([1,2,3])
        2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)
    
        Keyword arguments:
        :param Observable cls: Observable class
        :param Scheduler scheduler: [Optional] Scheduler to run the
            enumeration of the input sequence on.
    
        :returns: The observable sequence whose elements are pulled from the
            given enumerable sequence.
        :rtype: Observable
        """
        pass

    @classmethod
    def generate(cls, initial_state, condition, iterate, result_selector, scheduler=None):
        """
        Generates an observable sequence by running a state-driven loop
        producing the sequence's elements, using the specified scheduler to
        send out observer messages.
    
        1 - res = rx.Observable.generate(0,
            lambda x: x < 10,
            lambda x: x + 1,
            lambda x: x)
        2 - res = rx.Observable.generate(0,
            lambda x: x < 10,
            lambda x: x + 1,
            lambda x: x,
            Rx.Scheduler.timeout)
    
        Keyword arguments:
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning False).
        iterate -- Iteration step function.
        result_selector -- Selector function for results produced in the
            sequence.
        scheduler -- [Optional] Scheduler on which to run the generator loop.
            If not provided, defaults to CurrentThreadScheduler.
    
        Returns the generated sequence.
        """
        pass

    @classmethod
    def generate_with_relative_time(cls, initial_state, condition, iterate, result_selector, time_selector, scheduler=None):
        """
        Generates an observable sequence by iterating a state from an
        initial state until the condition fails.
    
        res = source.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: 500)
    
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning false).
        iterate -- Iteration step function.
        result_selector -- Selector function for results produced in the
            sequence.
        time_selector -- Time selector function to control the speed of values
            being produced each iteration, returning integer values denoting
            milliseconds.
        scheduler -- [Optional] Scheduler on which to run the generator loop.
            If not specified, the timeout scheduler is used.
    
        Returns the generated sequence.
        """
        pass

    def group_by(self, key_selector, element_selector=None, comparer=None):
        """
        Groups the elements of an observable sequence according to a
        specified key selector function and comparer and selects the resulting
        elements by using a specified function.
    
        1 - observable.group_by(lambda x: x.id)
        2 - observable.group_by(lambda x: x.id, lambda x: x.name)
        3 - observable.group_by(
            lambda x: x.id,
            lambda x: x.name,
            lambda x: str(x))
    
        Keyword arguments:
        key_selector -- A function to extract the key for each element.
        element_selector -- [Optional] A function to map each source element to
            an element in an observable group.
        comparer -- {Function} [Optional] Used to determine whether the objects
            are equal.
    
        Returns a sequence of observable groups, each of which corresponds to a
        unique key value, containing all elements that share that same key
        value.
        """
        pass

    def group_by_until(self, key_selector, element_selector, duration_selector, comparer=None):
        """
        Groups the elements of an observable sequence according to a
        specified key selector function. A duration selector function is used
        to control the lifetime of groups. When a group expires, it receives
        an OnCompleted notification. When a new element with the same key value
        as a reclaimed group occurs, the group will be reborn with a new
        lifetime request.
    
        1 - observable.group_by_until(
                lambda x: x.id,
                None,
                lambda : Rx.Observable.never()
            )
        2 - observable.group_by_until(
                lambda x: x.id,
                lambda x: x.name,
                lambda: Rx.Observable.never()
            )
        3 - observable.group_by_until(
                lambda x: x.id,
                lambda x: x.name,
                lambda:  Rx.Observable.never(),
                lambda x: str(x))
    
        Keyword arguments:
        key_selector -- A function to extract the key for each element.
        duration_selector -- A function to signal the expiration of a group.
        comparer -- [Optional] {Function} Used to compare objects. When not
            specified, the default comparer is used. Note: this argument will be
            ignored in the Python implementation of Rx. Python objects knows,
            or should know how to compare themselves.
    
        Returns a sequence of observable groups, each of which corresponds to
        a unique key value, containing all elements that share that same key
        value. If a group's lifetime expires, a new group with the same key
        value can be created once an element with such a key value is
        encountered.
        """
        pass

    def group_join(self, right, left_duration_selector, right_duration_selector, result_selector):
        """
        Correlates the elements of two sequences based on overlapping
        durations, and groups the results.
    
        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_selector -- A function to select the duration (expressed
            as an observable sequence) of each element of the left observable
            sequence, used to determine overlap.
        right_duration_selector -- A function to select the duration (expressed
            as an observable sequence) of each element of the right observable
            sequence, used to determine overlap.
        result_selector -- A function invoked to compute a result element for
            any element of the left sequence with overlapping elements from the
            right observable sequence. The first parameter passed to the
            function is an element of the left sequence. The second parameter
            passed to the function is an observable sequence with elements from
            the right sequence that overlap with the left sequence's element.
    
        Returns an observable sequence that contains result elements computed
        from source elements that have an overlapping duration.
        """
        pass

    @classmethod
    def if_then(cls, condition, then_source, else_source=None, scheduler=None):
        """
        Determines whether an observable collection contains values.
    
        Example:
        1 - res = rx.Observable.if(condition, obs1)
        2 - res = rx.Observable.if(condition, obs1, obs2)
        3 - res = rx.Observable.if(condition, obs1, scheduler=scheduler)
    
        Keyword parameters:
        condition -- {Function} The condition which determines if the
            then_source or else_source will be run.
        then_source -- {Observable} The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source -- {Observable} [Optional] The observable sequence or
            Promise that will be run if the condition function returns False.
            If this is not provided, it defaults to rx.Observable.empty
        scheduler -- [Optional] Scheduler to use.
    
        Returns an observable {Observable} sequence which is either the
        then_source or else_source.
        """
        pass

    def ignore_elements(self):
        """
        Ignores all elements in an observable sequence leaving only the
        termination messages.
    
        Returns an empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
        """
        pass

    @classmethod
    def interval(cls, period, scheduler=None):
        """
        Returns an observable sequence that produces a value after each
        period.
    
        Example:
        1 - res = rx.Observable.interval(1000)
        2 - res = rx.Observable.interval(1000, rx.Scheduler.timeout)
    
        Keyword arguments:
        period -- Period for producing the values in the resulting sequence
            (specified as an integer denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the timer on. If not specified,
            rx.Scheduler.timeout is used.
    
        Returns an observable sequence that produces a value after each period.
        """
        pass

    def is_empty(self):
        """
        Determines whether an observable sequence is empty.
    
        Returns an observable {Observable} sequence containing a single element
        determining whether the source sequence is empty.
        """
        pass

    def join(self, right, left_duration_selector, right_duration_selector, result_selector):
        """
        Correlates the elements of two sequences based on overlapping
        durations.
    
        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_selector -- A function to select the duration (expressed
            as an observable sequence) of each element of the left observable
            sequence, used to determine overlap.
        right_duration_selector -- A function to select the duration (expressed
            as an observable sequence) of each element of the right observable
            sequence, used to determine overlap.
        result_selector -- A function invoked to compute a result element for
            any two overlapping elements of the left and right observable
            sequences. The parameters passed to the function correspond with
            the elements from the left and right source sequences for which
            overlap occurs.
    
        Return an observable sequence that contains result elements computed
        from source elements that have an overlapping duration.
        """
        pass

    @classmethod
    def just(cls, value, scheduler=None):
        """
        Returns an observable sequence that contains a single element,
        using the specified scheduler to send out observer messages.
        There is an alias called 'just'.
    
        example
        res = rx.Observable.return(42)
        res = rx.Observable.return(42, rx.Scheduler.timeout)
    
        Keyword arguments:
        value -- Single element in the resulting observable sequence.
        scheduler -- [Optional] Scheduler to send the single element on. If
            not specified, defaults to Scheduler.immediate.
    
        Returns an observable sequence containing the single specified
        element.
        """
        pass

    def last(self, predicate=None):
        """
        Returns the last element of an observable sequence that satisfies the
        condition in the predicate if specified, else the last element.
    
        Example:
        res = source.last()
        res = source.last(lambda x: x > 3)
    
        Keyword arguments:
        predicate -- {Function} [Optional] A predicate function to evaluate for
            elements in the source sequence.
    
        Returns {Observable} Sequence containing the last element in the
        observable sequence that satisfies the condition in the predicate.
        """
        pass

    def last_or_default(self, predicate=None, default_value=None):
        """
        Return last or default element.
    
        Returns the last element of an observable sequence that satisfies
        the condition in the predicate, or a default value if no such
        element exists.
    
        Examples:
        res = source.last_or_default()
        res = source.last_or_default(lambda x: x > 3)
        res = source.last_or_default(lambda x: x > 3, 0)
        res = source.last_or_default(None, 0)
    
        predicate -- {Function} [Optional] A predicate function to evaluate
            for elements in the source sequence.
        default_value -- [Optional] The default value if no such element
            exists. If not specified, defaults to None.
    
        Returns {Observable} Sequence containing the last element in the
        observable sequence that satisfies the condition in the predicate,
        or a default value if no such element exists.
        """
        pass

    def let(self, func):
        """
        Returns an observable sequence that is the result of invoking the
        selector on the source sequence, without sharing subscriptions. This
        operator allows for a fluent style of writing queries that use the same
        sequence multiple times.
    
        selector -- {Function} Selector function which can use the source
            sequence as many times as needed, without sharing subscriptions to
            the source sequence.
    
        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        pass

    def let_bind(self, func):
        """
        Returns an observable sequence that is the result of invoking the
        selector on the source sequence, without sharing subscriptions. This
        operator allows for a fluent style of writing queries that use the same
        sequence multiple times.
    
        selector -- {Function} Selector function which can use the source
            sequence as many times as needed, without sharing subscriptions to
            the source sequence.
    
        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        pass

    def many_select(self, selector, scheduler=None):
        """
        Comonadic bind operator. Internally projects a new observable for each
        value, and it pushes each observable into the user-defined selector function
        that projects/queries each observable into some result.
    
        Keyword arguments:
        selector -- {Function} A transform function to apply to each element.
        scheduler -- {Object} [Optional] Scheduler used to execute the
            operation. If not specified, defaults to the ImmediateScheduler.
    
        Returns {Observable} An observable sequence which results from the
        comonadic bind operation.
        """
        pass

    def map(self, selector):
        """
        Project each element of an observable sequence into a new form
        by incorporating the element's index.
    
        1 - source.map(lambda value: value * value)
        2 - source.map(lambda value, index: value * value + index)
    
        Keyword arguments:
        :param Callable[[Any, Any], Any] selector: A transform function to
            apply to each source element; the second parameter of the
            function represents the index of the source element.
        :rtype: Observable
    
        Returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source.
        """
        pass

    def materialize(self):
        """
        Materializes the implicit notifications of an observable sequence as
        explicit notification values.
    
        Returns an observable sequence containing the materialized notification
        values from the source sequence.
        """
        pass

    def max(self, comparer=None):
        """
        Returns the maximum value in an observable sequence according to the
        specified comparer.
    
        Example
        res = source.max()
        res = source.max(lambda x, y:  x.value - y.value)
    
        Keyword arguments:
        comparer -- {Function} [Optional] Comparer used to compare elements.
    
        Returns {Observable} An observable sequence containing a single element
        with the maximum element in the source sequence.
        """
        pass

    def max_by(self, key_selector, comparer=None):
        """
        Returns the elements in an observable sequence with the maximum
        key value according to the specified comparer.
    
        Example
        res = source.max_by(lambda x: x.value)
        res = source.max_by(lambda x: x.value, lambda x, y: x - y)
    
        Keyword arguments:
        key_selector -- {Function} Key selector function.
        comparer -- {Function} [Optional] Comparer used to compare key values.
    
        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a maximum key value.
        """
        pass

    def median(self):
        """
        
        Calculates the statistical median on numerical emissions. The sequence must be finite.
        """
        pass

    @classmethod
    def merge(cls, *args, scheduler=None, sources):
        """
        Merges all the observable sequences into a single observable
        sequence. The scheduler is optional and if not specified, the
        immediate scheduler is used.
    
        1 - merged = rx.Observable.merge(xs, ys, zs)
        2 - merged = rx.Observable.merge([xs, ys, zs])
        3 - merged = rx.Observable.merge(scheduler, xs, ys, zs)
        4 - merged = rx.Observable.merge(scheduler, [xs, ys, zs])
    
        Returns the observable sequence that merges the elements of the
        observable sequences.
        """
        pass

    def merge_all(self):
        """
        Merges an observable sequence of observable sequences into an
        observable sequence.
    
        Returns the observable sequence that merges the elements of the inner
        sequences.
        """
        pass

    def merge_observable(self):
        """
        Merges an observable sequence of observable sequences into an
        observable sequence.
    
        Returns the observable sequence that merges the elements of the inner
        sequences.
        """
        pass

    def min(self, comparer=None):
        """
        Returns the minimum element in an observable sequence according to
        the optional comparer else a default greater than less than check.
    
        Example
        res = source.min()
        res = source.min(lambda x, y: x.value - y.value)
    
        comparer -- {Function} [Optional] Comparer used to compare elements.
    
        Returns an observable sequence {Observable} containing a single element
        with the minimum element in the source sequence.
        """
        pass

    def min_by(self, key_selector, comparer=None):
        """
        Returns the elements in an observable sequence with the minimum key
        value according to the specified comparer.
    
        Example
        res = source.min_by(lambda x: x.value)
        res = source.min_by(lambda x: x.value, lambda x, y: x - y)
    
        Keyword arguments:
        key_selector -- {Function} Key selector function.
        comparer -- {Function} [Optional] Comparer used to compare key values.
    
        Returns an observable {Observable} sequence containing a list of zero
        or more elements that have a minimum key value.
        """
        pass

    def mode(self):
        """
        
        Returns the most frequently emitted value (or "values" if they have the same number of occurrences).
        The sequence must be finite.
        """
        pass

    def multicast(self, subject, subject_selector, selector=None):
        """
        Multicasts the source sequence notifications through an instantiated
        subject into all uses of the sequence within a selector function. Each
        subscription to the resulting sequence causes a separate multicast
        invocation, exposing the sequence resulting from the selector function's
        invocation. For specializations with fixed subject types, see Publish,
        PublishLast, and Replay.
    
        Example:
        1 - res = source.multicast(observable)
        2 - res = source.multicast(subject_selector=lambda: Subject(),
                                   selector=lambda x: x)
    
        Keyword arguments:
        subject_selector -- {Function} Factory function to create an
            intermediate subject through which the source sequence's elements
            will be multicast to the selector function.
        subject -- Subject {Subject} to push source elements into.
        selector -- {Function} [Optional] Optional selector function which can
            use the multicasted source sequence subject to the policies enforced
            by the created subject. Specified only if subject_selector" is a
            factory function.
    
        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        pass

    @classmethod
    def never(cls):
        """
        Returns a non-terminating observable sequence, which can be used to
        denote an infinite duration (e.g. when using reactive joins).
    
        Returns an observable sequence whose observers will never get called.
        """
        pass

    def observe_on(self, scheduler=None):
        """
        Wraps the source sequence in order to run its observer callbacks on
        the specified scheduler.
    
        Keyword arguments:
        scheduler -- Scheduler to notify observers on.
    
        Returns the source sequence whose observations happen on the specified
        scheduler.
    
        This only invokes observer callbacks on a scheduler. In case the
        subscription and/or unsubscription actions have side-effects
        that require to be run on a scheduler, use subscribe_on.
        """
        pass

    @classmethod
    def of(cls, *args, **kwargs):
        """
        This method creates a new Observable instance with a variable number
        of arguments, regardless of number or type of the arguments.
    
        Example:
        res = rx.Observable.of(1,2,3)
    
        Returns the observable sequence whose elements are pulled from the given
        arguments
        """
        pass

    @classmethod
    def on_error_resume_next(cls, *args):
        """
        Continues an observable sequence that is terminated normally or by
        an exception with the next observable sequence.
    
        1 - res = Observable.on_error_resume_next(xs, ys, zs)
        2 - res = Observable.on_error_resume_next([xs, ys, zs])
    
        Returns an observable sequence that concatenates the source sequences,
        even if a sequence terminates exceptionally.
        """
        pass

    def pairwise(self):
        """
        Returns a new observable that triggers on the second and subsequent
        triggerings of the input observable. The Nth triggering of the input
        observable passes the arguments from the N-1th and Nth triggering as a
        pair. The argument passed to the N-1th triggering is held in hidden
        internal state until the Nth triggering occurs.
    
        Returns an observable {Observable} that triggers on successive pairs of
        observations from the input observable as an array.
        """
        pass

    def partition(self, predicate, published):
        """
        Returns two observables which partition the observations of the
        source by the given function. The first will trigger observations for
        those values for which the predicate returns true. The second will
        trigger observations for those values where the predicate returns false.
        The predicate is executed once for each subscribed observer. Both also
        propagate all error observations arising from the source and each
        completes when the source completes.
    
        Keyword arguments:
        predicate -- The function to determine which output Observable will
            trigger a particular observation.
    
        Returns a list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate returns False.
        """
        pass

    def pausable(self, pauser):
        """
        Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False.
    
        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable(pauser)
    
        Keyword parameters:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.
    
        Returns the observable {Observable} sequence which is paused based upon
        the pauser.
        """
        pass

    def pausable_buffered(self, subject):
        """
        Pauses the underlying observable sequence based upon the observable
        sequence which yields True/False, and yields the values that were
        buffered while paused.
    
        Example:
        pauser = rx.Subject()
        source = rx.Observable.interval(100).pausable_buffered(pauser)
    
        Keyword arguments:
        pauser -- {Observable} The observable sequence used to pause the
            underlying sequence.
    
        Returns the observable {Observable} sequence which is paused based upon
        the pauser."""
        pass

    def pluck(self, key):
        """
        Retrieves the value of a specified key using dict-like access (as in
        element[key]) from all elements in the Observable sequence.
    
        Keyword arguments:
        key {String} The key to pluck.
    
        Returns a new Observable {Observable} sequence of key values.
    
        To pluck an attribute of each element, use pluck_attr.
    
        """
        pass

    def pluck_attr(self, property):
        """
        Retrieves the value of a specified property (using getattr) from all
        elements in the Observable sequence.
    
        Keyword arguments:
        property {String} The property to pluck.
    
        Returns a new Observable {Observable} sequence of property values.
    
        To pluck values using dict-like access (as in element[key]) on each
        element, use pluck.
    
        """
        pass

    def publish(self, selector=None):
        """
        Returns an observable sequence that is the result of invoking the
        selector on a connectable observable sequence that shares a single
        subscription to the underlying sequence. This operator is a
        specialization of Multicast using a regular Subject.
    
        Example:
        res = source.publish()
        res = source.publish(lambda x: x)
    
        selector -- {Function} [Optional] Selector function which can use the
            multicasted source sequence as many times as needed, without causing
            multiple subscriptions to the source sequence. Subscribers to the
            given source will receive all notifications of the source from the
            time of the subscription on.
    
        Returns an observable {Observable} sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function."""
        pass

    def publish_value(self, initial_value, selector=None):
        """
        Returns an observable sequence that is the result of invoking the
        selector on a connectable observable sequence that shares a single
        subscription to the underlying sequence and starts with initial_value.
    
        This operator is a specialization of Multicast using a BehaviorSubject.
    
        Example:
        res = source.publish_value(42)
        res = source.publish_value(42, lambda x: x.map(lambda y: y * y))
    
        Keyword arguments:
        initial_value -- {Mixed} Initial value received by observers upon
            subscription.
        selector -- {Function} [Optional] Optional selector function which can
            use the multicasted source sequence as many times as needed, without
            causing multiple subscriptions to the source sequence. Subscribers
            to the given source will receive immediately receive the initial
            value, followed by all notifications of the source from the time of
            the subscription on.
    
        Returns {Observable} An observable sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        pass

    @classmethod
    def range(cls, start, count, scheduler=None):
        """
        Generates an observable sequence of integral numbers within a
        specified range, using the specified scheduler to send out observer
        messages.
    
        1 - res = Rx.Observable.range(0, 10)
        2 - res = Rx.Observable.range(0, 10, rx.Scheduler.timeout)
    
        Keyword arguments:
        start -- The value of the first integer in the sequence.
        count -- The number of sequential integers to generate.
        scheduler -- [Optional] Scheduler to run the generator loop on. If not
            specified, defaults to Scheduler.current_thread.
    
        Returns an observable sequence that contains a range of sequential
        integral numbers.
        """
        pass

    def reduce(self, accumulator, seed):
        """
        Applies an accumulator function over an observable sequence,
        returning the result of the aggregation as a single element in the
        result sequence. The specified seed value is used as the initial
        accumulator value.
    
        For aggregation behavior with incremental intermediate results, see
        Observable.scan.
    
        Example:
        1 - res = source.reduce(lambda acc, x: acc + x)
        2 - res = source.reduce(lambda acc, x: acc + x, 0)
    
        Keyword arguments:
        :param types.FunctionType accumulator: An accumulator function to be
            invoked on each element.
        :param T seed: Optional initial accumulator value.
    
        :returns: An observable sequence containing a single element with the
            final accumulator value.
        :rtype: Observable
        """
        pass

    @classmethod
    def repeat(cls, value, repeat_count=None, scheduler=None):
        """
        Generates an observable sequence that repeats the given element the
        specified number of times, using the specified scheduler to send out
        observer messages.
    
        1 - res = rx.Observable.repeat(42)
        2 - res = rx.Observable.repeat(42, 4)
        3 - res = rx.Observable.repeat(42, 4, Rx.Scheduler.timeout)
        4 - res = rx.Observable.repeat(42, None, Rx.Scheduler.timeout)
    
        Keyword arguments:
        value -- Element to repeat.
        repeat_count -- [Optional] Number of times to repeat the element. If not
            specified, repeats indefinitely.
        scheduler -- Scheduler to run the producer loop on. If not specified,
            defaults to ImmediateScheduler.
    
        Returns an observable sequence that repeats the given element the
        specified number of times."""
        pass

    def replay(self, selector=None, buffer_size=None, window=None, scheduler=None):
        """
        Returns an observable sequence that is the result of invoking the
        selector on a connectable observable sequence that shares a single
        subscription to the underlying sequence replaying notifications subject
        to a maximum time length for the replay buffer.
    
        This operator is a specialization of Multicast using a ReplaySubject.
    
        Example:
        res = source.replay(buffer_size=3)
        res = source.replay(buffer_size=3, window=500)
        res = source.replay(None, 3, 500, scheduler)
        res = source.replay(lambda x: x.take(6).repeat(), 3, 500, scheduler)
    
        Keyword arguments:
        selector -- [Optional] Selector function which can use the multicasted
            source sequence as many times as needed, without causing multiple
            subscriptions to the source sequence. Subscribers to the given
            source will receive all the notifications of the source subject to
            the specified replay buffer trimming policy.
        buffer_size -- [Optional] Maximum element count of the replay buffer.
        window -- [Optional] Maximum time length of the replay buffer.
        scheduler -- [Optional] Scheduler where connected observers within the
            selector function will be invoked on.
    
        Returns {Observable} An observable sequence that contains the elements
        of a sequence produced by multicasting the source sequence within a
        selector function.
        """
        pass

    def retry(self, retry_count=None):
        """
        Repeats the source observable sequence the specified number of times
        or until it successfully terminates. If the retry count is not
        specified, it retries indefinitely.
    
        1 - retried = retry.repeat()
        2 - retried = retry.repeat(42)
    
        retry_count -- [Optional] Number of times to retry the sequence. If not
        provided, retry the sequence indefinitely.
    
        Returns an observable sequence producing the elements of the given
        sequence repeatedly until it terminates successfully.
        """
        pass

    @classmethod
    def return_value(cls, value, scheduler=None):
        """
        Returns an observable sequence that contains a single element,
        using the specified scheduler to send out observer messages.
        There is an alias called 'just'.
    
        example
        res = rx.Observable.return(42)
        res = rx.Observable.return(42, rx.Scheduler.timeout)
    
        Keyword arguments:
        value -- Single element in the resulting observable sequence.
        scheduler -- [Optional] Scheduler to send the single element on. If
            not specified, defaults to Scheduler.immediate.
    
        Returns an observable sequence containing the single specified
        element.
        """
        pass

    def sample(self, interval, sampler, scheduler=None):
        """
        Samples the observable sequence at each interval.
    
        1 - res = source.sample(sample_observable) # Sampler tick sequence
        2 - res = source.sample(5000) # 5 seconds
        2 - res = source.sample(5000, rx.scheduler.timeout) # 5 seconds
    
        Keyword arguments:
        source -- Source sequence to sample.
        interval -- Interval at which to sample (specified as an integer
            denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the sampling timer on. If not
            specified, the timeout scheduler is used.
    
        Returns sampled observable sequence.
        """
        pass

    def scan(self, accumulator, seed=None):
        """
        Applies an accumulator function over an observable sequence and
        returns each intermediate result. The optional seed value is used as
        the initial accumulator value. For aggregation behavior with no
        intermediate results, see Observable.aggregate.
    
        1 - scanned = source.scan(lambda acc, x: acc + x)
        2 - scanned = source.scan(lambda acc, x: acc + x, 0)
    
        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each element.
        seed -- [Optional] The initial accumulator value.
    
        Returns an observable sequence containing the accumulated values.
        """
        pass

    def select(self, selector):
        """
        Project each element of an observable sequence into a new form
        by incorporating the element's index.
    
        1 - source.map(lambda value: value * value)
        2 - source.map(lambda value, index: value * value + index)
    
        Keyword arguments:
        :param Callable[[Any, Any], Any] selector: A transform function to
            apply to each source element; the second parameter of the
            function represents the index of the source element.
        :rtype: Observable
    
        Returns an observable sequence whose elements are the result of
        invoking the transform function on each element of source.
        """
        pass

    def select_many(self, selector, result_selector=None):
        """
        One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.
    
        1 - source.select_many(lambda x: Observable.range(0, x))
    
        Or:
        Projects each element of an observable sequence to an observable
        sequence, invokes the result selector for the source element and each
        of the corresponding inner sequence's elements, and merges the results
        into one observable sequence.
    
        1 - source.select_many(lambda x: Observable.range(0, x), lambda x, y: x + y)
    
        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.
    
        1 - source.select_many(Observable.from_([1,2,3]))
    
        Keyword arguments:
        selector -- A transform function to apply to each element or an
            observable sequence to project each element from the source
            sequence onto.
        result_selector -- [Optional] A transform function to apply to each
            element of the intermediate sequence.
    
        Returns an observable sequence whose elements are the result of
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence
        elements and their corresponding source element to a result element.
        """
        pass

    def select_switch(self, selector):
        """
        Projects each element of an observable sequence into a new sequence
        of observable sequences by incorporating the element's index and then
        transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.
    
        Keyword arguments:
        selector -- {Function} A transform function to apply to each source
            element; the second parameter of the function represents the index
            of the source element.
    
        Returns an observable {Observable} sequence whose elements are the
        result of invoking the transform function on each element of source
        producing an Observable of Observable sequences and that at any point in
        time produces the elements of the most recent inner observable sequence
        that has been received.
        """
        pass

    def sequence_equal(self, second, comparer=None):
        """
        Determines whether two sequences are equal by comparing the
        elements pairwise using a specified equality comparer.
    
        1 - res = source.sequence_equal([1,2,3])
        2 - res = source.sequence_equal([{ "value": 42 }], lambda x, y: x.value == y.value)
        3 - res = source.sequence_equal(Observable.return_value(42))
        4 - res = source.sequence_equal(Observable.return_value({ "value": 42 }), lambda x, y: x.value == y.value)
    
        second -- Second observable sequence or array to compare.
        comparer -- [Optional] Comparer used to compare elements of both sequences.
                    No guarantees on order of comparer arguments.
    
        Returns an observable sequence that contains a single element which
        indicates whether both sequences are of equal length and their
        corresponding elements are equal according to the specified equality
        comparer.
        """
        pass

    def share(self):
        """
        Share a single subscription among multple observers.
    
        Returns a new Observable that multicasts (shares) the original
        Observable. As long as there is at least one Subscriber this
        Observable will be subscribed and emitting data. When all
        subscribers have unsubscribed it will unsubscribe from the source
        Observable.
    
        This is an alias for Observable.publish().ref_count().
        """
        pass

    def single(self, predicate=None):
        """
        Returns the only element of an observable sequence that satisfies the
        condition in the optional predicate, and reports an exception if there
        is not exactly one element in the observable sequence.
    
        Example:
        res = source.single()
        res = source.single(lambda x: x == 42)
    
        Keyword arguments:
        predicate -- {Function} [Optional] A predicate function to evaluate for
            elements in the source sequence.
    
        Returns {Observable} Sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate.
        """
        pass

    def single_or_default(self, predicate, default_value=None):
        """
        Returns the only element of an observable sequence that matches the
        predicate, or a default value if no such element exists this method
        reports an exception if there is more than one element in the observable
        sequence.
    
        Example:
        res = source.single_or_default()
        res = source.single_or_default(lambda x: x == 42)
        res = source.single_or_default(lambda x: x == 42, 0)
        res = source.single_or_default(None, 0)
    
        Keyword arguments:
        predicate -- {Function} A predicate function to evaluate for elements in
            the source sequence.
        default_value -- [Optional] The default value if the index is outside
            the bounds of the source sequence.
    
        Returns {Observable} Sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate, or a
        default value if no such element exists.
        """
        pass

    def skip(self, count):
        """
        Bypasses a specified number of elements in an observable sequence
        and then returns the remaining elements.
    
        Keyword arguments:
        count -- The number of elements to skip before returning the remaining
            elements.
    
        Returns an observable sequence that contains the elements that occur
        after the specified index in the input sequence.
        """
        pass

    def skip_last(self, count):
        """
        Bypasses a specified number of elements at the end of an observable
        sequence.
    
        Description:
        This operator accumulates a queue with a length enough to store the
        first `count` elements. As more elements are received, elements are
        taken from the front of the queue and produced on the result sequence.
        This causes elements to be delayed.
    
        Keyword arguments
        count -- Number of elements to bypass at the end of the source sequence.
    
        Returns an observable {Observable} sequence containing the source
        sequence elements except for the bypassed ones at the end.
        """
        pass

    def skip_last_with_time(self, duration, scheduler=None):
        """
        Skips elements for the specified duration from the end of the
        observable source sequence, using the specified scheduler to run timers.
    
        1 - res = source.skip_last_with_time(5000)
        2 - res = source.skip_last_with_time(5000, scheduler)
    
        Description:
        This operator accumulates a queue with a length enough to store elements
        received during the initial duration window. As more elements are
        received, elements older than the specified duration are taken from the
        queue and produced on the result sequence. This causes elements to be
        delayed with duration.
    
        Keyword arguments:
        duration -- {Number} Duration for skipping elements from the end of the
            sequence.
        scheduler -- {Scheduler} [Optional]  Scheduler to run the timer on. If
            not specified, defaults to Rx.Scheduler.timeout
        Returns an observable {Observable} sequence with the elements skipped
        during the specified duration from the end of the source sequence.
        """
        pass

    def skip_until(self, other):
        """
        Returns the values from the source observable sequence only after
        the other observable sequence produces a value.
    
        other -- The observable sequence that triggers propagation of elements
            of the source sequence.
    
        Returns an observable sequence containing the elements of the source
        sequence starting from the point the other sequence triggered
        propagation.
        """
        pass

    def skip_until_with_time(self, start_time, scheduler=None):
        """
        Skips elements from the observable source sequence until the
        specified start time, using the specified scheduler to run timers.
        Errors produced by the source sequence are always forwarded to the
        result sequence, even if the error occurs before the start time.
    
        Examples:
        res = source.skip_until_with_time(new Date(), [optional scheduler]);
        res = source.skip_until_with_time(5000, [optional scheduler]);
    
        Keyword arguments:
        start_time -- Time to start taking elements from the source sequence. If
            this value is less than or equal to Date(), no elements will be
            skipped.
        scheduler -- Scheduler to run the timer on. If not specified, defaults
            to rx.Scheduler.timeout.
    
        Returns {Observable} An observable sequence with the elements skipped
        until the specified start time.
        """
        pass

    def skip_while(self, predicate):
        """
        Bypasses elements in an observable sequence as long as a specified
        condition is true and then returns the remaining elements. The
        element's index is used in the logic of the predicate function.
    
        1 - source.skip_while(lambda value: value < 10)
        2 - source.skip_while(lambda value, index: value < 10 or index < 10)
    
        predicate -- A function to test each element for a condition; the
            second parameter of the function represents the index of the
            source element.
    
        Returns an observable sequence that contains the elements from the
        input sequence starting at the first element in the linear series that
        does not pass the test specified by predicate.
        """
        pass

    def skip_with_time(self, duration, scheduler=None):
        """
        Skips elements for the specified duration from the start of the
        observable source sequence, using the specified scheduler to run timers.
    
        Example:
        1 - res = source.skip_with_time(5000, [optional scheduler])
    
        Description:
        Specifying a zero value for duration doesn't guarantee no elements will
        be dropped from the start of the source sequence. This is a side-effect
        of the asynchrony introduced by the scheduler, where the action that
        causes callbacks from the source sequence to be forwarded may not
        execute immediately, despite the zero due time.
    
        Errors produced by the source sequence are always forwarded to the
        result sequence, even if the error occurs before the duration.
    
        Keyword arguments:
        duration -- {Number} Duration for skipping elements from the start of
            the sequence.
        scheduler -- {Scheduler} Scheduler to run the timer on. If not
            specified, defaults to Rx.Scheduler.timeout.
    
        Returns n observable {Observable} sequence with the elements skipped
        during the specified duration from the start of the source sequence.
        """
        pass

    def slice(self, start, stop, step, source):
        """
        Slices the given observable. It is basically a wrapper around the
        operators skip(), skip_last(), take(), take_last() and filter().
    
        This marble diagram helps you remember how slices works with streams.
        Positive numbers is relative to the start of the events, while negative
        numbers are relative to the end (on_completed) of the stream.
    
        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1
    
        Example:
        result = source.slice(1, 10)
        result = source.slice(1, -2)
        result = source.slice(1, -1, 2)
    
        Keyword arguments:
        :param Observable self: Observable to slice
        :param int start: Number of elements to skip of take last
        :param int stop: Last element to take of skip last
        :param int step: Takes every step element. Must be larger than zero
    
        :returns: Returns a sliced observable sequence.
        :rtype: Observable
        """
        pass

    def some(self, predicate):
        """
        Determines whether some element of an observable sequence satisfies a
        condition if present, else if some items are in the sequence.
    
        Example:
        result = source.some()
        result = source.some(lambda x: x > 3)
    
        Keyword arguments:
        predicate -- A function to test each element for a condition.
    
        Returns {Observable} an observable sequence containing a single element
        determining whether some elements in the source sequence pass the test
        in the specified predicate if given, else if some items are in the
        sequence.
        """
        pass

    def standard_deviation(self):
        """
        
        Returns the standard deviation of the numerical emissions:
        The sequence must be finite.
        """
        pass

    @classmethod
    def start(cls, func, scheduler=None):
        """
        Invokes the specified function asynchronously on the specified
        scheduler, surfacing the result through an observable sequence.
    
        Example:
        res = rx.Observable.start(lambda: pprint('hello'))
        res = rx.Observable.start(lambda: pprint('hello'), rx.Scheduler.timeout)
    
        Keyword arguments:
        func -- {Function} Function to run asynchronously.
        scheduler -- {Scheduler} [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.
    
        Returns {Observable} An observable sequence exposing the function's
        result value, or an exception.
    
        Remarks:
        The function is called immediately, not during the subscription of the
        resulting sequence. Multiple subscriptions to the resulting sequence can
        observe the function's result.
        """
        pass

    @classmethod
    def start_async(cls, function_async, future, ex):
        """
        Invokes the asynchronous function, surfacing the result through an
        observable sequence.
    
        Keyword arguments:
        :param types.FunctionType function_async: Asynchronous function which
            returns a Future to run.
    
        :returns: An observable sequence exposing the function's result value, or an
            exception.
        :rtype: Observable
        """
        pass

    def start_with(self, scheduler=None, *args, **kw):
        """
        Prepends a sequence of values to an observable sequence with an
        optional scheduler and an argument list of values to prepend.
    
        1 - source.start_with(1, 2, 3)
        2 - source.start_with(Scheduler.timeout, 1, 2, 3)
    
        Returns the source sequence prepended with the specified values.
        """
        pass

    def subscribe_on(self, scheduler=None):
        """
        Subscribe on the specified scheduler.
    
        Wrap the source sequence in order to run its subscription and
        unsubscription logic on the specified scheduler. This operation is not
        commonly used; see the remarks section for more information on the
        distinction between subscribe_on and observe_on.
    
        Keyword arguments:
        scheduler -- Scheduler to perform subscription and unsubscription
            actions on.
    
        Returns the source sequence whose subscriptions and unsubscriptions
        happen on the specified scheduler.
    
        This only performs the side-effects of subscription and unsubscription
        on the specified scheduler. In order to invoke observer callbacks on a
        scheduler, use observe_on.
        """
        pass

    def sum(self, key_selector=None):
        """
        Computes the sum of a sequence of values that are obtained by
        invoking an optional transform function on each element of the input
        sequence, else if not specified computes the sum on each item in the
        sequence.
    
        Example
        res = source.sum()
        res = source.sum(lambda x: x.value)
    
        key_selector -- {Function} [Optional] A transform function to apply to
            each element.
    
        Returns an observable {Observable} sequence containing a single element
        with the sum of the values in the source sequence.
        """
        pass

    @classmethod
    def switch_case(cls, selector, sources, default_source, scheduler=None):
        """
        Uses selector to determine which source in sources to use.
        There is an alias 'switch_case'.
    
        Example:
        1 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 })
        2 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 }, obs0)
        3 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 },
                                     scheduler=scheduler)
    
        Keyword arguments:
        :param types.FunctionType selector: The function which extracts the value
            for to test in a case statement.
        :param list sources: A object which has keys which correspond to the case
            statement labels.
        :param Observable default_source: The observable sequence or Promise that
            will be run if the sources are not matched. If this is not provided, it
            defaults to rx.Observabe.empty with the specified scheduler.
    
        :returns: An observable sequence which is determined by a case statement.
        :rtype: Observable
        """
        pass

    def switch_latest(self):
        """
        Transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.
    
        :returns: The observable sequence that at any point in time produces the
        elements of the most recent inner observable sequence that has been
        received.
        :rtype: Observable
        """
        pass

    def switch_map(self, selector):
        """
        Projects each element of an observable sequence into a new sequence
        of observable sequences by incorporating the element's index and then
        transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.
    
        Keyword arguments:
        selector -- {Function} A transform function to apply to each source
            element; the second parameter of the function represents the index
            of the source element.
    
        Returns an observable {Observable} sequence whose elements are the
        result of invoking the transform function on each element of source
        producing an Observable of Observable sequences and that at any point in
        time produces the elements of the most recent inner observable sequence
        that has been received.
        """
        pass

    def take(self, count, scheduler=None):
        """
        Returns a specified number of contiguous elements from the start of
        an observable sequence, using the specified scheduler for the edge case
        of take(0).
    
        1 - source.take(5)
        2 - source.take(0, rx.Scheduler.timeout)
    
        Keyword arguments:
        count -- The number of elements to return.
        scheduler -- [Optional] Scheduler used to produce an OnCompleted
            message in case count is set to 0.
    
        Returns an observable sequence that contains the specified number of
        elements from the start of the input sequence.
        """
        pass

    def take_last(self, count):
        """
        Returns a specified number of contiguous elements from the end of an
        observable sequence.
    
        Example:
        res = source.take_last(5)
    
        Description:
        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence, this
        buffer is drained on the result sequence. This causes the elements to be
        delayed.
    
        Keyword arguments:
        :param int count: Number of elements to take from the end of the source
            sequence.
    
        :returns: An observable sequence containing the specified number of elements 
            from the end of the source sequence.
        :rtype: Observable
        """
        pass

    def take_last_buffer(self, count):
        """
        Returns an array with the specified number of contiguous elements
        from the end of an observable sequence.
    
        Example:
        res = source.take_last(5)
    
        Description:
        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence, this
        buffer is drained on the result sequence. This causes the elements to be
        delayed.
    
        Keyword arguments:
        :param int count: Number of elements to take from the end of the source
            sequence.
    
        :returns: An observable sequence containing a single list with the specified 
        number of elements from the end of the source sequence.
        :rtype: Observable
        """
        pass

    def take_last_with_time(self, duration, scheduler=None):
        """
        Returns elements within the specified duration from the end of the
        observable source sequence, using the specified schedulers to run timers
        and to drain the collected elements.
    
        Example:
        res = source.take_last_with_time(5000, scheduler)
    
        Description:
        This operator accumulates a queue with a length enough to store elements
        received during the initial duration window. As more elements are
        received, elements older than the specified duration are taken from the
        queue and produced on the result sequence. This causes elements to be
        delayed with duration.
    
        Keyword arguments:
        duration -- {Number} Duration for taking elements from the end of the
            sequence.
        scheduler -- {Scheduler} [Optional] Scheduler to run the timer on. If
            not specified, defaults to rx.Scheduler.timeout.
    
        Returns {Observable} An observable sequence with the elements taken
        during the specified duration from the end of the source sequence.
        """
        pass

    def take_until(self, other):
        """
        Returns the values from the source observable sequence until the
        other observable sequence produces a value.
    
        Keyword arguments:
        other -- Observable sequence that terminates propagation of elements of
            the source sequence.
    
        Returns an observable sequence containing the elements of the source
        sequence up to the point the other sequence interrupted further
        propagation.
        """
        pass

    def take_until_with_time(self, end_time, scheduler=None):
        """
        Takes elements for the specified duration until the specified end
        time, using the specified scheduler to run timers.
    
        Examples:
        1 - res = source.take_until_with_time(dt, [optional scheduler])
        2 - res = source.take_until_with_time(5000, [optional scheduler])
    
        Keyword Arguments:
        end_time -- {Number | Date} Time to stop taking elements from the source
            sequence. If this value is less than or equal to Date(), the
            result stream will complete immediately.
        scheduler -- {Scheduler} Scheduler to run the timer on.
    
        Returns an observable {Observable} sequence with the elements taken
        until the specified end time.
        """
        pass

    def take_while(self, predicate):
        """
        Returns elements from an observable sequence as long as a specified
        condition is true. The element's index is used in the logic of the
        predicate function.
    
        1 - source.take_while(lambda value: value < 10)
        2 - source.take_while(lambda value, index: value < 10 or index < 10)
    
        Keyword arguments:
        predicate -- A function to test each element for a condition; the
            second parameter of the function represents the index of the source
            element.
    
        Returns an observable sequence that contains the elements from the
        input sequence that occur before the element at which the test no
        longer passes.
        """
        pass

    def take_with_time(self, duration, scheduler=None):
        """
        Takes elements for the specified duration from the start of the
        observable source sequence, using the specified scheduler to run timers.
    
        Example:
        res = source.take_with_time(5000,  [optional scheduler])
    
        Description:
        This operator accumulates a queue with a length enough to store elements
        received during the initial duration window. As more elements are
        received, elements older than the specified duration are taken from the
        queue and produced on the result sequence. This causes elements to be
        delayed with duration.
    
        Keyword arguments:
        duration -- {Number} Duration for taking elements from the start of the
            sequence.
        scheduler -- {Scheduler} Scheduler to run the timer on. If not
            specified, defaults to rx.Scheduler.timeout.
    
        Returns {Observable} An observable sequence with the elements taken
        during the specified duration from the start of the source sequence.
        """
        pass

    def tap(self, on_next=None, on_error=None, on_completed=None, observer=None):
        """
        Invokes an action for each element in the observable sequence and
        invokes an action on graceful or exceptional termination of the
        observable sequence. This method can be used for debugging, logging,
        etc. of query behavior by intercepting the message stream to run
        arbitrary actions for messages on the pipeline.
    
        1 - observable.do_action(observer)
        2 - observable.do_action(on_next)
        3 - observable.do_action(on_next, on_error)
        4 - observable.do_action(on_next, on_error, on_completed)
    
        observer -- [Optional] Observer, or ...
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke on exceptional termination
            of the observable sequence.
        on_completed -- [Optional] Action to invoke on graceful termination
            of the observable sequence.
    
        Returns the source sequence with the side-effecting behavior applied.
        """
        pass

    def then(self, selector):
        """
        Matches when the observable sequence has an available value and projects
        the value.
    
        :param types.FunctionType selector: Selector that will be invoked for values
            in the source sequence.
        :returns: Plan that produces the projected values, to be fed (with other
            plans) to the when operator.
        :rtype: Plan
        """
        pass

    def then_do(self, selector):
        """
        Matches when the observable sequence has an available value and projects
        the value.
    
        :param types.FunctionType selector: Selector that will be invoked for values
            in the source sequence.
        :returns: Plan that produces the projected values, to be fed (with other
            plans) to the when operator.
        :rtype: Plan
        """
        pass

    def throttle_first(self, window_duration, scheduler=None):
        """
        Returns an Observable that emits only the first item emitted by the
        source Observable during sequential time windows of a specified
        duration.
    
        Keyword arguments:
        window_duration -- {timedelta} time to wait before emitting another item
            after emitting the last item.
        scheduler -- {Scheduler} [Optional] the Scheduler to use internally to
            manage the timers that handle timeout for each item. If not
            provided, defaults to Scheduler.timeout.
        Returns {Observable} An Observable that performs the throttle operation.
        """
        pass

    def throttle_last(self, interval, sampler, scheduler=None):
        """
        Samples the observable sequence at each interval.
    
        1 - res = source.sample(sample_observable) # Sampler tick sequence
        2 - res = source.sample(5000) # 5 seconds
        2 - res = source.sample(5000, rx.scheduler.timeout) # 5 seconds
    
        Keyword arguments:
        source -- Source sequence to sample.
        interval -- Interval at which to sample (specified as an integer
            denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the sampling timer on. If not
            specified, the timeout scheduler is used.
    
        Returns sampled observable sequence.
        """
        pass

    def throttle_with_selector(self, throttle_duration_selector):
        """
        Ignores values from an observable sequence which are followed by
        another value within a computed throttle duration.
    
        1 - res = source.throttle_with_selector(lambda x: rx.Scheduler.timer(x+x))
    
        Keyword arguments:
        throttle_duration_selector -- Selector function to retrieve a sequence
            indicating the throttle duration for each given element.
    
        Returns the throttled sequence.
        """
        pass

    def throttle_with_timeout(self, duetime, scheduler=None):
        """
        Ignores values from an observable sequence which are followed by
        another value before duetime.
    
        Example:
        1 - res = source.debounce(5000) # 5 seconds
        2 - res = source.debounce(5000, scheduler)
    
        Keyword arguments:
        duetime -- {Number} Duration of the throttle period for each value
            (specified as an integer denoting milliseconds).
        scheduler -- {Scheduler} [Optional]  Scheduler to run the throttle
            timers on. If not specified, the timeout scheduler is used.
    
        Returns {Observable} The debounced sequence.
        """
        pass

    @classmethod
    def throw(cls, exception, scheduler=None):
        """
        Returns an observable sequence that terminates with an exception,
        using the specified scheduler to send out the single OnError message.
    
        1 - res = rx.Observable.throw_exception(Exception('Error'))
        2 - res = rx.Observable.throw_exception(Exception('Error'),
                                                rx.Scheduler.timeout)
    
        Keyword arguments:
        exception -- An object used for the sequence's termination.
        scheduler -- Scheduler to send the exceptional termination call on. If
            not specified, defaults to ImmediateScheduler.
    
        Returns the observable sequence that terminates exceptionally with the
        specified exception object.
        """
        pass

    @classmethod
    def throw_exception(cls, exception, scheduler=None):
        """
        Returns an observable sequence that terminates with an exception,
        using the specified scheduler to send out the single OnError message.
    
        1 - res = rx.Observable.throw_exception(Exception('Error'))
        2 - res = rx.Observable.throw_exception(Exception('Error'),
                                                rx.Scheduler.timeout)
    
        Keyword arguments:
        exception -- An object used for the sequence's termination.
        scheduler -- Scheduler to send the exceptional termination call on. If
            not specified, defaults to ImmediateScheduler.
    
        Returns the observable sequence that terminates exceptionally with the
        specified exception object.
        """
        pass

    def time_interval(self, scheduler=None):
        """
        Records the time interval between consecutive values in an
        observable sequence.
    
        1 - res = source.time_interval();
        2 - res = source.time_interval(Scheduler.timeout)
    
        Keyword arguments:
        scheduler -- [Optional] Scheduler used to compute time intervals. If
            not specified, the timeout scheduler is used.
    
        Return An observable sequence with time interval information on values.
        """
        pass

    def timeout(self, duetime, other, scheduler=None):
        """
        Returns the source observable sequence or the other observable
        sequence if duetime elapses.
    
        1 - res = source.timeout(new Date()); # As a date
        2 - res = source.timeout(5000); # 5 seconds
        # As a date and timeout observable
        3 - res = source.timeout(datetime(), rx.Observable.return_value(42))
        # 5 seconds and timeout observable
        4 - res = source.timeout(5000, rx.Observable.return_value(42))
        # As a date and timeout observable
        5 - res = source.timeout(datetime(), rx.Observable.return_value(42),
                                 rx.Scheduler.timeout)
        # 5 seconds and timeout observable
        6 - res = source.timeout(5000, rx.Observable.return_value(42),
                                 rx.Scheduler.timeout)
    
        Keyword arguments:
        :param datetime|int duetime: Absolute (specified as a datetime object) or
            relative time (specified as an integer denoting milliseconds) when a
            timeout occurs.
        :param Observable other: Sequence to return in case of a timeout. If not
            specified, a timeout error throwing sequence will be used.
        :param Scheduler scheduler: Scheduler to run the timeout timers on. If not
            specified, the timeout scheduler is used.
    
        :returns: The source sequence switching to the other sequence in case of
            a timeout.
        :rtype: Observable
        """
        pass

    def timeout_with_selector(self, first_timeout=None, timeout_duration_selector=None, other=None):
        """
        Returns the source observable sequence, switching to the other
        observable sequence if a timeout is signaled.
    
        1 - res = source.timeout_with_selector(rx.Observable.timer(500))
        2 - res = source.timeout_with_selector(rx.Observable.timer(500),
                    lambda x: rx.Observable.timer(200))
        3 - res = source.timeout_with_selector(rx.Observable.timer(500),
                    lambda x: rx.Observable.timer(200)),
                    rx.Observable.return_value(42))
    
        first_timeout -- [Optional] Observable sequence that represents the
            timeout for the first element. If not provided, this defaults to
            Observable.never().
        timeout_Duration_selector -- [Optional] Selector to retrieve an
            observable sequence that represents the timeout between the current
            element and the next element.
        other -- [Optional] Sequence to return in case of a timeout. If not
            provided, this is set to Observable.throw_exception().
    
        Returns the source sequence switching to the other sequence in case of
        a timeout.
        """
        pass

    @classmethod
    def timer(cls, duetime, period=None, scheduler=None):
        """
        Returns an observable sequence that produces a value after duetime
        has elapsed and then after each period.
    
        1 - res = Observable.timer(datetime(...))
        2 - res = Observable.timer(datetime(...), 1000)
        3 - res = Observable.timer(datetime(...), Scheduler.timeout)
        4 - res = Observable.timer(datetime(...), 1000, Scheduler.timeout)
    
        5 - res = Observable.timer(5000)
        6 - res = Observable.timer(5000, 1000)
        7 - res = Observable.timer(5000, scheduler=Scheduler.timeout)
        8 - res = Observable.timer(5000, 1000, Scheduler.timeout)
    
        Keyword arguments:
        duetime -- Absolute (specified as a Date object) or relative time
            (specified as an integer denoting milliseconds) at which to produce
            the first value.</param>
        period -- [Optional] Period to produce subsequent values (specified as
            an integer denoting milliseconds), or the scheduler to run the
            timer on. If not specified, the resulting timer is not recurring.
        scheduler -- [Optional] Scheduler to run the timer on. If not
            specified, the timeout scheduler is used.
    
        Returns an observable sequence that produces a value after due time has
        elapsed and then each period.
        """
        pass

    def timestamp(self, scheduler=None):
        """
        Records the timestamp for each value in an observable sequence.
    
        1 - res = source.timestamp() # produces objects with attributes "value" and
            "timestamp", where value is the original value.
        2 - res = source.timestamp(Scheduler.timeout)
    
        :param Scheduler scheduler: [Optional] Scheduler used to compute timestamps. If not
            specified, the timeout scheduler is used.
    
        Returns an observable sequence with timestamp information on values.
        """
        pass

    @classmethod
    def to_async(cls, func, scheduler=None):
        """
        Converts the function into an asynchronous function. Each invocation
        of the resulting asynchronous function causes an invocation of the
        original synchronous function on the specified scheduler.
    
        Example:
        res = Observable.to_async(lambda x, y: x + y)(4, 3)
        res = Observable.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        res = Observable.to_async(lambda x: log.debug(x),
                                  Scheduler.timeout)('hello')
    
        func -- {Function} Function to convert to an asynchronous function.
        scheduler -- {Scheduler} [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.
    
        Returns {Function} Asynchronous function.
        """
        pass

    def to_blocking(self):
        pass

    def to_dict(self, key_selector, element_selector=None):
        """
        Converts the observable sequence to a Map if it exists.
    
        Keyword arguments:
        key_selector -- {Function} A function which produces the key for the
            Map.
        element_selector -- {Function} [Optional] An optional function which
            produces the element for the Map. If not present, defaults to the
            value from the observable sequence.
        Returns {Observable} An observable sequence with a single value of a Map
        containing the values from the observable sequence.
        """
        pass

    def to_future(self, future_ctor=None):
        """
        Converts an existing observable sequence to a Future
    
        Example:
        future = rx.Observable.return_value(42).to_future(trollius.Future);
    
        With config:
        rx.config["Future"] = trollius.Future
        future = rx.Observable.return_value(42).to_future()
    
        future_ctor -- {Function} [Optional] The constructor of the future.
            If not provided, it looks for it in rx.config.Future.
    
        Returns {Future} An future with the last value from the observable
        sequence.
        """
        pass

    def to_iterable(self, accumulator):
        """
        Creates a list from an observable sequence.
    
        Returns an observable sequence containing a single element with a list
        containing all the elements of the source sequence."""
        pass

    def to_list(self, accumulator):
        """
        Creates a list from an observable sequence.
    
        Returns an observable sequence containing a single element with a list
        containing all the elements of the source sequence."""
        pass

    def to_set(self):
        """
        Converts the observable sequence to a set.
    
        Returns {Observable} An observable sequence with a single value of a set
        containing the values from the observable sequence.
        """
        pass

    def to_sorted_list(self, key_selector, reverse):
        """
        
        Creates a sorted list from an observable sequence,
        with an optional key_selector used to map the attribute for sorting
    
        Returns an observable sequence containing a single element with a list
        containing all the sorted elements of the source sequence."""
        pass

    def transduce(self, transducer):
        """
        Execute a transducer to transform the observable sequence.
    
        Keyword arguments:
        :param Transducer transducer: A transducer to execute.
    
        :returns: An Observable sequence containing the results from the
            transducer.
        :rtype: Observable
        """
        pass

    @classmethod
    def using(cls, resource_factory, observable_factory):
        """
        Constructs an observable sequence that depends on a resource object,
        whose lifetime is tied to the resulting observable sequence's lifetime.
    
        1 - res = rx.Observable.using(lambda: AsyncSubject(), lambda: s: s)
    
        Keyword arguments:
        resource_factory -- Factory function to obtain a resource object.
        observable_factory -- Factory function to obtain an observable sequence
            that depends on the obtained resource.
    
        Returns an observable sequence whose lifetime controls the lifetime of
        the dependent resource object.
        """
        pass

    def variance(self, squared_values):
        """
        
        Returns the statistical variance of the numerical emissions.
        The sequence must be finite.
        """
        pass

    @classmethod
    def when(cls, *args):
        """
        Joins together the results from several patterns.
    
        :param Observable cls: Observable class.
        :param list[Plan] args: A series of plans (specified as a list of as a
            series of arguments) created by use of the Then operator on patterns.
        :returns: Observable sequence with the results form matching several
            patterns.
        :rtype: Observable
        """
        pass

    def where(self, predicate):
        """
        Filters the elements of an observable sequence based on a predicate
        by incorporating the element's index.
    
        1 - source.filter(lambda value: value < 10)
        2 - source.filter(lambda value, index: value < 10 or index < 10)
    
        Keyword arguments:
        :param Observable self: Observable sequence to filter.
        :param (T, <int>) -> bool predicate: A function to test each source element
            for a condition; the
            second parameter of the function represents the index of the source
            element.
    
        :returns: An observable sequence that contains elements from the input
        sequence that satisfy the condition.
        :rtype: Observable
        """
        pass

    @classmethod
    def while_do(cls, condition, source):
        """
        Repeats source as long as condition holds emulating a while loop.
    
        Keyword arguments:
        :param types.FunctionType condition: The condition which determines if the
            source will be repeated.
        :param Observable source: The observable sequence that will be run if the
            condition function returns true.
    
        :returns: An observable sequence which is repeated as long as the condition
            holds.
        :rtype: Observable
        """
        pass

    def window(self, window_openings, window_closing_selector=None):
        """
        Projects each element of an observable sequence into zero or more
        windows.
    
        Keyword arguments:
        :param Observable window_openings: Observable sequence whose elements
            denote the creation of windows.
        :param types.FunctionType window_closing_selector: [Optional] A function
            invoked to define the closing of each produced window. It defines the
            boundaries of the produced windows (a window is started when the
            previous one is closed, resulting in non-overlapping windows).
    
        :returns: An observable sequence of windows.
        :rtype: Observable[Observable]
        """
        pass

    def window_with_count(self, count, skip=None):
        """
        Projects each element of an observable sequence into zero or more
        windows which are produced based on element count information.
    
        1 - xs.window_with_count(10)
        2 - xs.window_with_count(10, 1)
    
        count -- Length of each window.
        skip -- [Optional] Number of elements to skip between creation of
            consecutive windows. If not specified, defaults to the count.
    
        Returns an observable sequence of windows.
        """
        pass

    def window_with_time(self, timespan, timeshift, scheduler=None):
        pass

    def window_with_time_or_count(self, timespan, count, scheduler=None):
        pass

    @classmethod
    def with_latest_from(cls, *args):
        """
        Merges the specified observable sequences into one observable sequence
        by using the selector function only when the first observable sequence
        produces an element. The observables can be passed either as seperate
        arguments or as a list.
    
        1 - obs = Observable.with_latest_from(obs1, obs2, obs3,
                                           lambda o1, o2, o3: o1 + o2 + o3)
        2 - obs = Observable.with_latest_from([obs1, obs2, obs3],
                                            lambda o1, o2, o3: o1 + o2 + o3)
    
        Returns an observable sequence containing the result of combining
        elements of the sources using the specified result selector function.
        """
        pass

    @classmethod
    def zip(cls, *args, first):
        """
        Merges the specified observable sequences into one observable
        sequence by using the selector function whenever all of the observable
        sequences have produced an element at a corresponding index.
    
        The last element in the arguments must be a function to invoke for each
        series of elements at corresponding indexes in the sources.
    
        Arguments:
        args -- Observable sources.
    
        Returns an observable {Observable} sequence containing the result of
        combining elements of the sources using the specified result selector
        function.
        """
        pass

    @classmethod
    def zip_array(cls, *args):
        """
        Merge the specified observable sequences into one observable
        sequence by emitting a list with the elements of the observable
        sequences at corresponding indexes.
    
        Keyword arguments:
        :param Observable cls: Class
        :param Tuple args: Observable sources.
    
        :return: Returns an observable sequence containing lists of
        elements at corresponding indexes.
        :rtype: Observable
        """
        pass

    @classmethod
    def zip_list(cls, *args):
        """
        Merge the specified observable sequences into one observable
        sequence by emitting a list with the elements of the observable
        sequences at corresponding indexes.
    
        Keyword arguments:
        :param Observable cls: Class
        :param Tuple args: Observable sources.
    
        :return: Returns an observable sequence containing lists of
        elements at corresponding indexes.
        :rtype: Observable
        """
        pass