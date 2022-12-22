Testing
-------

Using the tools provided in `reactivex.testing`, it is possible to create tests for 
your own observables, custom operators and subscriptions.

Additionally, tests can be used to help understand the behaviors of existing operators.

Basic example
.............

.. code:: python

    # Import the testing tools
    from reactivex.testing import ReactiveTest, TestScheduler
    from reactivex import operators

    # setting up aliases for more concise code
    on_next = ReactiveTest.on_next
    on_error = ReactiveTest.on_error
    on_completed = ReactiveTest.on_completed
    subscribe = ReactiveTest.subscribe


    # This assumes that you are using pytest but unittest or others would work just as well

    from reactivex.testing import ReactiveTest, TestScheduler
    from reactivex import operators

    on_next = ReactiveTest.on_next
    on_error = ReactiveTest.on_error
    on_completed = ReactiveTest.on_completed
    subscribe = ReactiveTest.subscribe


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

Surprised about the timestamps (@500, @600, ...) for the result messages? Read below about the timeline

Timeline
........

When `scheduler.start` is called, the test scheduler starts moving its virtual clock forward.
Some important timestamps are however hidden as defaults, as listed below.
These values can be modified using kwargs in the `scheduler.start(...)` call:

1. ``created`` [100]: When is the observable created. 
That is when the ``create`` function seen in the basic example, or the lambda above is called.
2. `subscribed` [200]: When does the subscription occur. 
This explains the above emission timestamps: 
consider the first emission @500; given that we are using a cold observable,
and subscribe to it at 200, the "source"'s timeline starts at 200 and only 300 ticks later, it emits.
1. `disposed` [1000]: When the subscription is disposed

Keep the following in mind when modifying these values:

1. Do not use `0` as values since the code ignores that
2. If you change `subscribed` to be lower than 100, you need to change `created` as well
otherwise nothing will happen.


Testing an observable factory
.............................

An observable created from `Observable(subscribe)` can be just as easily tested. 
Let's use this example to additionally test a disposal case

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

Going back to the in_sequence_or_throw_ operator, we did not test the error case

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
        # Often it's better not to test the exact exception; we can test a specific emit as follows:
        message, err = result.messages
        assert message.time == 130
        assert err.time == 230
        assert message.value.kind == 'N'  # Notification
        assert err.value.kind == 'E'  # E for errors
        assert message.value.value == 1
        assert type(err.value.exception) == ValueError  # look at .exception for errors


Testing subscriptions, multiple observables, hot observables
..............................................

``scheduler.start`` only allows for a single subscription. 
Some cases like e.g. `operators.partition` require more.
The examples below showcase some less commonly needed testing tools.
