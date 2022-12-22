Testing
-------

Using the tools provided in `reactivex.testing`, it is possible to create tests for 
your own observables, custom operators and subscriptions.

Additionally, tests can be used to help understand the behaviors of existing operators.

Basic example
.............

.. code:: python

    # This assumes that you are using pytest but unittest or others would work just as well
    # Import the testing tools
    from reactivex.testing import ReactiveTest, TestScheduler
    from reactivex import operators

    # setting up aliases for more concise code
    on_next = ReactiveTest.on_next
    on_error = ReactiveTest.on_error
    on_completed = ReactiveTest.on_completed

    def test_double():
        # Create a scheduler
        scheduler = TestScheduler()
        # Define one or more source
        source = scheduler.create_hot_observable(
            on_next(250, 3),
            on_next(350, 5),
        )

        # Define how the observable/operator is used on the source
        def create():
            return source.pipe(operators.map(lambda x: 2 * x))

        # trigger subscription and record emissions
        results = scheduler.start(create)

        # check the messages and potentially subscriptions
        assert results.messages == [
            on_next(250, 6),
            on_next(350, 10),
        ]


Testing a custom operator
.........................

Whether your custom operator is created using a *composition* of operators 
or with full control, you can easily test various situations and combinations

.. _in_sequence_or_throw:

.. code:: python

    def test_operator():
        # Code to test; takes a sequence of integers and passes through,
        # unless they are not in sequence in which case it errors
        def in_sequence_or_throw():
            return reactivex.compose(
                operators.start_with(None),
                operators.pairwise(),
                operators.flat_map(lambda x: reactivex.of(x[1]) if (
                    x[0] is None or x[1] == x[0] + 1
                ) else reactivex.throw(ValueError('Sequence error')))
            )
        ## End of code to test

        scheduler = TestScheduler()
        # Create source
        source = scheduler.create_cold_observable(
            on_next(300, 1), on_next(400, 2), on_next(500, 3), on_completed(600)
        )
        # Here is another way to create the same observable, 
        # as long as we set the correct scheduler
        source = reactivex.from_marbles('------1-2-3-|', timespan=50, scheduler=scheduler)
        # You can shorten the "create" function from the basic example to a lambda with no arguments
        result = scheduler.start(lambda: source.pipe(
            in_sequence_or_throw(),
        ))
        assert result.messages == [
            on_next(500, 1), on_next(600, 2), on_next(700, 3), on_completed(800)
        ]

Surprised about the timestamps (@500, @600, ...) for the result messages? 
Then read below about the timeline.

Timeline
........

When ``scheduler.start`` is called, the test scheduler starts moving its virtual clock forward.
Some important timestamps are however hidden as defaults, as listed below.
These values can be modified using kwargs in the ``scheduler.start(...)`` call:

1. ``created`` [100]: When is the observable created. 
   That is when the ``create`` function seen in the basic example.
2. ``subscribed`` [200]: When does the subscription occur. 
   This explains the above emission timestamps: 
   consider the first emission @500; given that we are using a cold observable,
   and subscribe to it at 200, the "source"'s timeline starts at 200 and only 300 ticks later, it emits.
3. ``disposed`` [1000]: When the subscription is disposed

Keep the following in mind when modifying these values:

1. Do not use `0` as values since the code ignores that
2. If you change ``subscribed`` to be lower than 100, you need to change ``created`` as well
   otherwise nothing will happen.

An alternative using marbles
............................

As we saw in the previous section, we can use `reactivex.from_marbles` 
to create observables for our tests.

An example of using `to_marbles` for the assertion is shown in test_hot_

There is a simplified flow available in `reactivex.testing.marbles` and here's an example:

.. code:: python
    
    def test_start_with():
        from reactivex.testing.marbles import marbles_testing
        with marbles_testing() as (start, cold, hot, exp):
            source = cold('------1-2-3-|')
            outcome = exp('a-----1-2-3-|', {"a": None})  # can use lookups if needed
            obs = source.pipe(
                operators.start_with(None)
            )
            # Note that start accepts the observable directly, 
            # without the need for a "create" function
            results = start(obs)  
            
            assert results == outcome

This method makes for very quick to write, and easy to read, tests.


Testing an observable factory
.............................

An observable created from `Observable(subscribe)` can be just as easily tested. 
Let's use this example to additionally test a Disposable case.

.. code:: python

    def test_my_observable_factory():
        from reactivex.disposable import Disposable, CompositeDisposable
        a = 42
        def factory(observer: Observer, scheduler=None):
            def increment():
                nonlocal a
                a += 1
            sub = Disposable(action=increment)
            return CompositeDisposable(
                sub,
                reactivex.timer(20, scheduler=scheduler).subscribe(observer)
            )

        scheduler = TestScheduler()
        result = scheduler.start(lambda: Observable(factory))
        assert result.messages == [
            on_next(220, 0),
            on_completed(220)
        ]
        assert a == 43


Testing errors
..............

Going back to the in_sequence_or_throw_ operator, we did not test the error case;
Let's remedy that below.

.. code:: python

    def test_in_sequence_or_throw_error():
        scheduler = TestScheduler()
        source = reactivex.from_marbles('--1-4-3-', timespan=50, scheduler=scheduler)
        result = scheduler.start(lambda: source.pipe(
            in_sequence_or_throw(),
        ), created=1, subscribed=30)

        assert result.messages == [
            on_next(30+100, 1),
            on_error(230, ValueError('Sequence error'))
        ]
        # At times it's better not to test the exact exception, 
        # maybe its message changes with time or other reasons
        # We can test a specific notification's details as follows:
        message, err = result.messages
        assert message.time == 130
        assert err.time == 230
        assert message.value.kind == 'N'  # Notification
        assert err.value.kind == 'E'  # E for errors
        assert message.value.value == 1
        assert type(err.value.exception) == ValueError  # look at .exception for errors


Testing subscriptions, multiple observables, hot observables
............................................................

``scheduler.start`` only allows for a single subscription. 
Some cases like e.g. `operators.partition` require more.
The examples below showcase some less commonly needed testing tools.

.. code:: python
    
    def test_multiple():
        scheduler = TestScheduler()
        source = reactivex.from_marbles('-1-4-3-|', timespan=50, scheduler=scheduler)
        odd, even = source.pipe(
            operators.partition(lambda x: x % 2),
        )
        steven = scheduler.create_observer()
        todd = scheduler.create_observer()

        even.subscribe(steven)
        odd.subscribe(todd)

        # Note! Since it's not "start" which creates the subscription, they actually occur at t=0
        scheduler.start()

        assert steven.messages == [
            on_next(150, 4),
            on_completed(350)
        ]
        assert todd.messages == [
            on_next(50, 1),
            on_next(250, 3),
            on_completed(350)
        ]


.. code:: python

    from reactivex.testing.subscription import Subscription
    def test_subscriptions():
        scheduler = TestScheduler()
        source = scheduler.create_cold_observable()  # "infinite"
        subs = []
        shared = source.pipe(
            operators.share()
        )
        """first sub"""
        scheduler.schedule_relative(200, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))
        # second sub, should not sub to source itself
        scheduler.schedule_relative(300, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))
        scheduler.schedule_relative(500, lambda *_: subs[1].dispose())
        scheduler.schedule_relative(600, lambda *_: subs[0].dispose())
        """end first sub"""
        # no existing sub should sub again onto source - we never dispose of it
        scheduler.schedule_relative(900, lambda *_: subs.append(shared.subscribe(scheduler=scheduler)))

        scheduler.start()
        # Check that the submissions on the source are as expected
        assert source.subscriptions == [
            Subscription(200, 600),
            Subscription(900),  # represents an infinite subscription
        ]

.. _test_hot:

.. code:: python

    def test_hot():
        scheduler = TestScheduler()
        # hot starts at 0 but sub starts at 200 so we'll miss 190
        source = scheduler.create_hot_observable(
            on_next(190, 5),
            on_next(300, 42),
            on_completed(500)
        )
        result = scheduler.start(lambda: source.pipe(
            operators.to_marbles(timespan=20, scheduler=scheduler)
        ))

        message = result.messages[0]
        # the subscription starts at 200;
        # since `source` is a hot observable, the notification @190 will not be caught
        # the next notification is at 300 ticks, 
        # which, on our subscription, will show at 100 ticks (300-200 from subscribed)
        # or 5 "-" each representing 20 ticks (timespan=20 in to_marbles)
        # then the 42 is received
        # and then nothing for another 200 ticks, so 10 "-" before complete
        assert message.value.value == '-----(42)----------|'

