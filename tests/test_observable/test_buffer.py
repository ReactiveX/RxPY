import unittest

from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest
from rx.testing.marbles import marbles_testing

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBuffer(unittest.TestCase):

    def test_buffer_simple(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_next(400, True),
            on_next(500, True),
            on_completed(900)
        )

        def create():
            return xs.pipe(ops.buffer(ys))

        res = scheduler.start(create=create)

        assert [
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_next(400, lambda b: b == []),
            on_next(500, lambda b: b == [7, 8, 9]),
            on_next(590, lambda b: b == [10]),
            on_completed(590)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 590)]

        assert ys.subscriptions == [
            subscribe(200, 590)]

    def test_buffer_closeboundaries(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_completed(400)
        )

        def create():
            return xs.pipe(ops.buffer(ys))

        res = scheduler.start(create=create)

        assert [
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_next(400, lambda b: b == []),
            on_completed(400)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]

    def test_buffer_throwsource(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(380, 7),
            on_error(400, ex)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_completed(500)
        )

        def create():
            return xs.pipe(ops.buffer(ys))

        res = scheduler.start(create=create)

        assert [
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_error(400, ex)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]

    def test_buffer_throwboundaries(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(90, 1),
            on_next(180, 2),
            on_next(250, 3),
            on_next(260, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(410, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_next(550, 10),
            on_completed(590)
        )

        ys = scheduler.create_hot_observable(
            on_next(255, True),
            on_next(330, True),
            on_next(350, True),
            on_error(400, ex)
        )

        def create():
            return xs.pipe(ops.buffer(ys))
        res = scheduler.start(create=create)

        assert [
            on_next(255, lambda b: b == [3]),
            on_next(330, lambda b: b == [4, 5]),
            on_next(350, lambda b: b == [6]),
            on_error(400, ex)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]

    def test_when_closing_with_empty_observable(self):
        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            def closing_mapper():
                return cold('-----|')

            lookup = {'a': [1, 2], 'b': [3], 'c': [4, 5], 'd': [6], 'e': [7]}
            #               -----|
            #                    -----|
            #                         -----|
            #                              -----|
            #                                   -----|
            source = hot('  -1--2---3--4--5--6---7--|')
            expected = exp('-----a----b----c----d---(e,|)', lookup=lookup)
            #               012345678901234567890123456789
            #               0         1         2
            obs = source.pipe(ops.buffer_when(closing_mapper))
            results = start(obs)
            assert results == expected

    def test_when_closing_only_on_first_item(self):
        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            def closing_mapper():
                return cold('-----1--2--3--4--|')

            lookup = {'a': [1, 2], 'b': [3], 'c': [4, 5], 'd': [6], 'e': [7]}
            #               -----1--2--3--4--|
            #                    -----1--2--3--4--|
            #                         -----1--2--3--4--|
            #                              -----1--2--3--4--|
            source = hot('  -1--2---3--4--5--6---7--|')
            expected = exp('-----a----b----c----d---(e,|)', lookup=lookup)
            #               012345678901234567890123456789
            #               0         1         2
            obs = source.pipe(ops.buffer_when(closing_mapper))
            results = start(obs)
            assert results == expected

    def test_when_source_on_error(self):
        class TestException(Exception):
            pass

        ex = TestException('test exception')

        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            def closing_mapper():
                return cold('-----1|')

            lookup = {'a': [1, 2], 'b': [3], 'c': [4, 5], 'd': [6], 'e': [7]}
            #               -----1|
            #                    -----1|
            #                         -----1|
            #                              -----1|
            #                                   -----1|
            source = hot('  -1--2---3--4--5--#', error=ex)
            expected = exp('-----a----b----c-#', lookup=lookup, error=ex)
            #               012345678901234567890123456789
            #               0         1         2

            obs = source.pipe(ops.buffer_when(closing_mapper))
            results = start(obs)
            assert results == expected

    def test_when_closing_on_error(self):
        class TestException(Exception):
            pass

        ex = TestException('test exception')

        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            def closing_mapper():
                return cold('-----#', error=ex)

            #               -----#
            source = hot('  -1--2---3--4--5--6---7--|')
            expected = exp('-----#', error=ex)
            #               012345678901234567890123456789
            #               0         1         2
            obs = source.pipe(ops.buffer_when(closing_mapper))
            results = start(obs)
            assert results == expected

    def test_toggle_closing_with_empty_observable(self):
        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            lookup = {'a': [2, 3], 'b': [5], 'c': [7], 'd': [8, 9]}

            openings = hot('---a-------b------c---d-------|')
            a = cold('         ------|')
            b = cold('                 ----|')
            c = cold('                        ---|')
            d = cold('                            -----|')
            source = hot('  -1--2--3--4--5--6---7--8--9---|')
            expected = exp('---------a-----b-----c-----d--|', lookup=lookup)
            #               012345678901234567890123456789
            #               0         1         2
            closings = {'a': a, 'b': b, 'c': c, 'd': d}

            def closing_mapper(key):
                return closings[key]

            obs = source.pipe(ops.buffer_toggle(openings, closing_mapper))
            results = start(obs)
            assert results == expected

    def test_toggle_closing_with_only_first_item(self):
        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            lookup = {'a': [2, 3], 'b': [5], 'c': [7], 'd': [8, 9]}

            openings = hot('---a-------b------c---d-------|')
            a = cold('         ------1-2-|')
            b = cold('                 ----1-2-|')
            c = cold('                        ---1-2-|')
            d = cold('                            -----1-2|')
            source = hot('  -1--2--3--4--5--6---7--8--9---|')
            expected = exp('---------a-----b-----c-----d--|', lookup=lookup)
            #               012345678901234567890123456789
            #               0         1         2
            closings = {'a': a, 'b': b, 'c': c, 'd': d}

            def closing_mapper(key):
                return closings[key]

            obs = source.pipe(ops.buffer_toggle(openings, closing_mapper))
            results = start(obs)
            assert results == expected

    def test_toggle_source_on_error(self):
        class TestException(Exception):
            pass

        ex = TestException('test exception')

        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            lookup = {'a': [2, 3], 'b': [5], 'c': [7], 'd': [8, 9]}

            openings = hot('---a-------b------c---d-------|')
            a = cold('         ------1-2-|')
            b = cold('                 ----1-2-|')
            c = cold('                        ---1-2-|')
            d = cold('                            -----1-2|')
            source = hot('  -1--2--3--4--5--6--#', error=ex)
            expected = exp('---------a-----b---#', lookup=lookup, error=ex)
            #               012345678901234567890123456789
            #               0         1         2
            closings = {'a': a, 'b': b, 'c': c, 'd': d}

            def closing_mapper(key):
                return closings[key]

            obs = source.pipe(ops.buffer_toggle(openings, closing_mapper))
            results = start(obs)
            assert results == expected

    def test_toggle_openings_on_error(self):
        class TestException(Exception):
            pass

        ex = TestException('test exception')

        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            lookup = {'a': [2, 3], 'b': [5], 'c': [7], 'd': [8, 9]}

            openings = hot('---a-------b-----#', error=ex)
            a = cold('         ------1|')
            b = cold('                 ----1|')
            c = cold('                        ---1|')
            d = cold('                            -----1|')
            source = hot('  -1--2--3--4--5--6---7--8--9---|')
            expected = exp('---------a-----b-#', lookup=lookup, error=ex)
            #               012345678901234567890123456789
            #               0         1         2
            closings = {'a': a, 'b': b, 'c': c, 'd': d}

            def closing_mapper(key):
                return closings[key]

            obs = source.pipe(ops.buffer_toggle(openings, closing_mapper))
            results = start(obs)
            assert results == expected

    def test_toggle_closing_mapper_on_error(self):
        class TestException(Exception):
            pass

        ex = TestException('test exception')

        with marbles_testing(timespan=1.0) as (start, cold, hot, exp):

            lookup = {'a': [2, 3], 'b': [5], 'c': [7], 'd': [8, 9]}

            openings = hot('---a-------b------c---d-------|')
            a = cold('         ------1|')
            b = cold('                 ---#', error=ex)
            c = cold('                        ---1|')
            d = cold('                            -----1|')
            source = hot('  -1--2--3--4--5--6---7--8--9---|')
            expected = exp('---------a----#', lookup=lookup, error=ex)
            #               012345678901234567890123456789
            #               0         1         2
            closings = {'a': a, 'b': b, 'c': c, 'd': d}

            def closing_mapper(key):
                return closings[key]

            obs = source.pipe(ops.buffer_toggle(openings, closing_mapper))
            results = start(obs)
            assert results == expected
