import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToDict(unittest.TestCase):

    def test_to_dict_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            close(660)
        )

        def create():
            return xs.to_dict(lambda x: x * 2, lambda x: x * 4)

        res = scheduler.start(create)
        print(res.messages)
        res.messages.assert_equal(
            send(660, {4: 8, 6: 12, 8: 16, 10: 20}),
            close(660)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 660)
        )

    def test_to_dict_error(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            throw(660, ex)
        )

        def create():
            return xs.to_dict(lambda x: x * 2, lambda x: x * 4)

        res = scheduler.start(create)

        res.messages.assert_equal(
            throw(660, ex)
        )

        xs.subscriptions.assert_equal(
           subscribe(200, 660)
        )


    def test_to_dict_keyselectorthrows(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            close(600)
          )

        def create():
            def key_selector(x):
                if x < 4:
                    return x * 2
                else:
                    raise ex
            return xs.to_dict(key_selector, lambda x: x * 4)

        res = scheduler.start(create)

        res.messages.assert_equal(
            throw(440, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 440)
        )

    def test_to_dict_elementselectorthrows(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            close(600)
        )

        def value_selector(x):
            if x < 4:
                return x * 4
            else:
                raise ex

        def create():
            return xs.to_dict(lambda x: x * 2 , value_selector)

        res = scheduler.start(create)

        res.messages.assert_equal(
            throw(440, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 440)
        )

    def test_to_dict_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5)
        )

        def create():
            return xs.to_dict(lambda x: x * 2, lambda x: x * 4)

        res = scheduler.start(create)

        res.messages.assert_equal()

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )
