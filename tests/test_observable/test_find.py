import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestFind(unittest.TestCase):

    def test_find_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1)
        )

        def create():
            return xs.find(lambda x,i,s: True)

        res = scheduler.start(create)

        assert res.messages == []

    def test_find_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            close(210)
        )

        def create():
            return xs.find(lambda x,i,s: True)

        res = scheduler.start(create)

        assert res.messages == [
            send(210, None),
            close(210)]

    def test_find_single(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            close(220)
        )

        def create():
            return xs.find(lambda x,i,s: x==2)
        res = scheduler.start(create)

        assert res.messages == [
            send(210, 2),
            close(210)]

    def test_find_notfound(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            close(220)
        )

        def create():
            return xs.find(lambda x,i,s: x==3)
        res = scheduler.start(create)

        assert res.messages == [
            send(220, None),
            close(220)]

    def test_find_Error(self):
        ex = Exception('error')
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            throw(220, ex)
        )

        def create():
            return xs.find(lambda x,i,s: x==3)
        res = scheduler.start(create)

        assert res.messages == [
            throw(220, ex)]

    def test_find_throws(self):
        ex = 'error'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            close(220)
        )

        def create():
            def predicate(x, i, source):
                raise Exception(ex)
            return xs.find(predicate)
        res = scheduler.start(create)

        assert res.messages == [
            throw(210, ex)]
