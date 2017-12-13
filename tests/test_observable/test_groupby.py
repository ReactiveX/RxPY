import math
import unittest
from datetime import datetime

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

class TestGroupBy(unittest.TestCase):
    def test_group_by_with_key_comparer(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            close(570),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()

            return xs.group_by(key_selector, lambda x: x).map(lambda g: g.key)

        results = scheduler.start(factory)
        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"),
            send(360, "qux"),
            close(570))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)

    def test_groupby_outer_complete(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            close(570),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()

            def element_selector(x):
                ele_invoked[0] += 1
                return x[::-1] # Yes, this is reverse string in Python

            return xs.group_by(key_selector, element_selector).map(lambda g: g.key)

        results = scheduler.start(factory)
        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"),
            send(360, "qux"),
            close(570))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)
        assert(ele_invoked[0] == 12)

    def test_group_by_outer_error(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            throw(570, ex),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()
            def element_selector(x):
                ele_invoked[0] += 1
                return x[::-1]

            return xs.group_by(key_selector, element_selector).map(lambda g: g.key)

        results = scheduler.start(factory)

        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"),
            send(360, "qux"),
            throw(570, ex))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)
        assert(ele_invoked[0] == 12)


    def test_group_by_outer_dispose(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            close(570),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()

            def element_selector(x):
                ele_invoked[0] += 1
                return x[::-1]

            return xs.group_by(key_selector, element_selector).map(lambda g: g.key)

        results = scheduler.start(factory, disposed=355)

        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"))
        xs.subscriptions.assert_equal(subscribe(200, 355))
        assert(key_invoked[0] == 5)
        assert(ele_invoked[0] == 5)

    def test_group_by_outer_key_throw(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            close(570),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))
        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                if key_invoked[0] == 10:
                    raise Exception(ex)

                return x.lower().strip()

            def element_selector(x):
                ele_invoked[0] += 1
                return x[::-1]

            return xs.group_by(key_selector, element_selector).map(lambda g: g.key)

        results = scheduler.start(factory)
        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"),
            send(360, "qux"),
            throw(480, ex))
        xs.subscriptions.assert_equal(subscribe(200, 480))
        assert(key_invoked[0] == 10)
        assert(ele_invoked[0] == 9)

    def test_group_by_outer_ele_throw(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            send(90, "error"),
            send(110, "error"),
            send(130, "error"),
            send(220, "  foo"),
            send(240, " FoO "),
            send(270, "baR  "),
            send(310, "foO "),
            send(350, " Baz   "),
            send(360, "  qux "),
            send(390, "   bar"),
            send(420, " BAR  "),
            send(470, "FOO "),
            send(480, "baz  "),
            send(510, " bAZ "),
            send(530, "    fOo    "),
            close(570),
            send(580, "error"),
            close(600),
            throw(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()

            def element_selector(x):
                ele_invoked[0] += 1
                if ele_invoked[0] == 10:
                    raise Exception(ex)
                return x[::-1]

            return xs.group_by(key_selector, element_selector).map(lambda g: g.key)

        results = scheduler.start(factory)
        results.messages.assert_equal(
            send(220, "foo"),
            send(270, "bar"),
            send(350, "baz"),
            send(360, "qux"),
            throw(480, ex))
        xs.subscriptions.assert_equal(subscribe(200, 480))
        assert(key_invoked[0] == 10)
        assert(ele_invoked[0] == 10)

    # def test_group_by_inner_complete(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(
    #         send(90, "error"),
    #         send(110, "error"),
    #         send(130, "error"),
    #         send(220, "  foo"),
    #         send(240, " FoO "),
    #         send(270, "baR  "),
    #         send(310, "foO "),
    #         send(350, " Baz   "),
    #         send(360, "  qux "),
    #         send(390, "   bar"),
    #         send(420, " BAR  "),
    #         send(470, "FOO "),
    #         send(480, "baz  "),
    #         send(510, " bAZ "),
    #         send(530, "    fOo    "),
    #         close(570),
    #         send(580, "error"),
    #         close(600),
    #         throw(650, 'ex'))
    #     c = {
    #         "outer_subscription": None,
    #         "inner_subscriptions": {},
    #         "inners": {},
    #         "results": {},
    #         "outer": None
    #     }

    #     def action1(scheduler, state):
    #         c["outer"] = xs.group_by(lambda x: x.lower().strip(), lambda x: x[::-1])

    #     scheduler.schedule_absolute(created, action1)

    #     def action2(scheduler, state):

    #         def next(group):

    #             result = scheduler.create_observer()
    #             c["inners"][group.key] = group
    #             c["results"][group.key] = result

    #             def action21(scheduler, state):
    #                 c["inner_subscriptions"][group.key] = group.subscribe(result, scheduler)

    #             scheduler.schedule_relative(100, action21)
    #         c["outer_subscription"] = c["outer"].subscribe_callbacks(next, scheduler=scheduler)
    #     scheduler.schedule_absolute(subscribed, action2)

    #     def action3(scheduler, state):
    #         c["outer_subscription"].dispose()
    #         for sub in c["inner_subscriptions"].values():
    #             sub.dispose()

    #     scheduler.schedule_absolute(disposed, action3)
    #     scheduler.start()
    #     assert(len(c["inners"]) == 4)
    #     c["results"]['foo'].messages.assert_equal(
    #         send(470, " OOF"),
    #         send(530, "    oOf    "),
    #         close(570))
    #     c["results"]['bar'].messages.assert_equal(
    #         send(390, "rab   "),
    #         send(420, "  RAB "),
    #         close(570))
    #     c["results"]['baz'].messages.assert_equal(
    #         send(480, "  zab"),
    #         send(510, " ZAb "),
    #         close(570))
    #     c["results"]['qux'].messages.assert_equal(
    #         close(570))
    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 570))

    # def test_group_by_inner_complete_all(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(
    #         send(90, "error"),
    #         send(110, "error"),
    #         send(130, "error"),
    #         send(220, "  foo"),
    #         send(240, " FoO "),
    #         send(270, "baR  "),
    #         send(310, "foO "),
    #         send(350, " Baz   "),
    #         send(360, "  qux "),
    #         send(390, "   bar"),
    #         send(420, " BAR  "),
    #         send(470, "FOO "),
    #         send(480, "baz  "),
    #         send(510, " bAZ "),
    #         send(530, "    fOo    "),
    #         close(570),
    #         send(580, "error"),
    #         close(600),
    #         throw(650, 'ex'))
    #     inners = {}
    #     inner_subscriptions = {}
    #     results = {}
    #     c = {
    #         "outer": None,
    #         "outer_subscription": None,
    #         "result": None
    #     }

    #     def action1(scheduler, state):
    #         c["outer"] = xs.group_by(
    #             lambda x: x.lower().strip(),
    #             lambda x: x[::-1]
    #         )
    #         return c["outer"]
    #     scheduler.schedule_absolute(created, action1)

    #     def action2(scheduler, state):
    #         def send(group):
    #             c["result"] = scheduler.create_observer()
    #             inners[group.key] = group
    #             results[group.key] = c["result"]
    #             inner_subscriptions[group.key] = group.subscribe(c["result"], scheduler)
    #         c["outer_subscription"] = c["outer"].subscribe_callbacks(send, scheduler=scheduler)
    #         return c["outer_subscription"]
    #     scheduler.schedule_absolute(subscribed, action2)

    #     def action3(scheduler, state):
    #         c["outer_subscription"].dispose()
    #         for sub in inner_subscriptions.values():
    #             sub.dispose()
    #     scheduler.schedule_absolute(disposed, action3)

    #     scheduler.start()
    #     assert(len(inners) == 4)
    #     results['foo'].messages.assert_equal(
    #         send(220, "oof  "),
    #         send(240, " OoF "),
    #         send(310, " Oof"),
    #         send(470, " OOF"),
    #         send(530, "    oOf    "),
    #         close(570))
    #     results['bar'].messages.assert_equal(
    #         send(270, "  Rab"),
    #         send(390, "rab   "),
    #         send(420, "  RAB "),
    #         close(570))
    #     results['baz'].messages.assert_equal(
    #         send(350, "   zaB "),
    #         send(480, "  zab"),
    #         send(510, " ZAb "),
    #         close(570))
    #     results['qux'].messages.assert_equal(
    #         send(360, " xuq  "),
    #         close(570))
    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 570))

    # def test_group_by_inner_error(self):
    #     ex = 'ex1'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(
    #         send(90, "error"),
    #         send(110, "error"),
    #         send(130, "error"),
    #         send(220, "  foo"),
    #         send(240, " FoO "),
    #         send(270, "baR  "),
    #         send(310, "foO "),
    #         send(350, " Baz   "),
    #         send(360, "  qux "),
    #         send(390, "   bar"),
    #         send(420, " BAR  "),
    #         send(470, "FOO "),
    #         send(480, "baz  "),
    #         send(510, " bAZ "),
    #         send(530, "    fOo    "),
    #         throw(570, ex),
    #         send(580, "error"),
    #         close(600),
    #         throw(650, 'ex'))
    #     inner_subscriptions = {}
    #     inners = {}
    #     results = {}
    #     c = {
    #         "outer_subscription": None,
    #         "outer": None
    #     }

    #     def action1(scheduler, state):
    #         c["outer"] = xs.group_by(
    #             lambda x: x.lower().strip(),
    #             lambda x: x[::-1]
    #         )
    #         return c["outer"]
    #     scheduler.schedule_absolute(created, action1)

    #     def action2(scheduler, state):
    #         def send(group):
    #             result = scheduler.create_observer()
    #             inners[group.key] = group
    #             results[group.key] = result

    #             def action3(scheduler, state):
    #                 inner_subscriptions[group.key] = group.subscribe(result, scheduler)

    #             scheduler.schedule_relative(100, action3)
    #         c["outer_subscription"] = c["outer"].subscribe_callbacks(send, lambda e: None, scheduler=scheduler)
    #         return c["outer_subscription"]
    #     scheduler.schedule_absolute(subscribed, action2)

    #     def action4(scheduler, state):
    #         c["outer_subscription"].dispose();
    #         for sub in inner_subscriptions.values():
    #             sub.dispose()
    #     scheduler.schedule_absolute(disposed, action4)

    #     scheduler.start()
    #     assert(len(inners) == 4)
    #     results['foo'].messages.assert_equal(
    #         send(470, " OOF"),
    #         send(530, "    oOf    "),
    #         throw(570, ex))
    #     results['bar'].messages.assert_equal(
    #         send(390, "rab   "),
    #         send(420, "  RAB "),
    #         throw(570, ex))
    #     results['baz'].messages.assert_equal(
    #         send(480, "  zab"),
    #         send(510, " ZAb "),
    #         throw(570, ex))
    #     results['qux'].messages.assert_equal(
    #         throw(570, ex))
    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 570))

    # def test_group_by_with_merge(self):
    #     scheduler = TestScheduler()

    #     xs = [None]
    #     results = [None]

    #     def selector(group):
    #         print("selector", group)
    #         return group.do_action(lambda x: print(x)).to_list()

    #     def action1(scheduler, state):
    #         xs[0] = Observable.from_(["alpha", "apple", "beta", "bat", "gamma"]) \
    #                           .group_by(lambda s: s[0]) \
    #                           .map(selector) \
    #                           .merge_all()
    #     scheduler.schedule_absolute(created, action1)

    #     def action2(scheduler, state):
    #         results[0] = scheduler.create_observer()
    #         xs[0].subscribe(results[0], scheduler)
    #     scheduler.schedule_absolute(subscribed, action2)

    #     scheduler.start()

    #     results[0].messages.assert_equal(
    #         send(200, ["alpha", "apple"]),
    #         send(200, ["beta", "bat"]),
    #         send(200, ["gamma"]),
    #         close(200))

if __name__ == '__main__':
    unittest.main()
