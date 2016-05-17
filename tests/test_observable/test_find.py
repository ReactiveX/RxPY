import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestFind(unittest.TestCase):

    def test_find_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1)
        )

        def create():
            return xs.find(lambda x,i,s: True)

        res = scheduler.start(create)

        res.messages.assert_equal(
        )

    def test_find_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_completed(210)
        )

        def create():
            return xs.find(lambda x,i,s: True)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(210, None),
            on_completed(210)
        )

    def test_find_single(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_completed(220)
        )

        def create():
            return xs.find(lambda x,i,s: x==2)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(210, 2),
            on_completed(210)
        )

    def test_find_notfound(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_completed(220)
        )

        def create():
            return xs.find(lambda x,i,s: x==3)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(220, None),
            on_completed(220)
        )

    def test_find_Error(self):
        ex = Exception('error')
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_error(220, ex)
        )

        def create():
            return xs.find(lambda x,i,s: x==3)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(220, ex)
        )

    def test_find_throws(self):
        ex = 'error'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_completed(220)
        )

        def create():
            def predicate(x, i, source):
                raise Exception(ex)
            return xs.find(predicate)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(210, ex)
        )
