import math
import unittest
from datetime import datetime

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
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
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))

        def factory():
            def key_selector(x):
                key_invoked[0] += 1
                return x.lower().strip()

            return xs.group_by(key_selector, lambda x: x).map(lambda g: g.key)

        results = scheduler.start(factory)
        results.messages.assert_equal(
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"),
            on_next(360, "qux"),
            on_completed(570))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)

    def test_groupby_outer_complete(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))

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
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"),
            on_next(360, "qux"),
            on_completed(570))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)
        assert(ele_invoked[0] == 12)

    def test_group_by_outer_error(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_error(570, ex),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))

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
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"),
            on_next(360, "qux"),
            on_error(570, ex))
        xs.subscriptions.assert_equal(subscribe(200, 570))
        assert(key_invoked[0] == 12)
        assert(ele_invoked[0] == 12)


    def test_group_by_outer_dispose(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))

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
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"))
        xs.subscriptions.assert_equal(subscribe(200, 355))
        assert(key_invoked[0] == 5)
        assert(ele_invoked[0] == 5)

    def test_group_by_outer_key_throw(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))
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
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"),
            on_next(360, "qux"),
            on_error(480, ex))
        xs.subscriptions.assert_equal(subscribe(200, 480))
        assert(key_invoked[0] == 10)
        assert(ele_invoked[0] == 9)

    def test_group_by_outer_ele_throw(self):
        scheduler = TestScheduler()
        key_invoked = [0]
        ele_invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))

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
            on_next(220, "foo"),
            on_next(270, "bar"),
            on_next(350, "baz"),
            on_next(360, "qux"),
            on_error(480, ex))
        xs.subscriptions.assert_equal(subscribe(200, 480))
        assert(key_invoked[0] == 10)
        assert(ele_invoked[0] == 10)

    def test_group_by_inner_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))
        c = {
            "outer_subscription": None,
            "inner_subscriptions": {},
            "inners": {},
            "results": {},
            "outer": None
        }

        def action1(scheduler, state):
            c["outer"] = xs.group_by(lambda x: x.lower().strip(), lambda x: x[::-1])

        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):

            def next(group):

                result = scheduler.create_observer()
                c["inners"][group.key] = group
                c["results"][group.key] = result

                def action21(scheduler, state):
                    c["inner_subscriptions"][group.key] = group.subscribe(result)

                scheduler.schedule_relative(100, action21)
            c["outer_subscription"] = c["outer"].subscribe(next)
        scheduler.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            c["outer_subscription"].dispose()
            for sub in c["inner_subscriptions"].values():
                sub.dispose()

        scheduler.schedule_absolute(disposed, action3)
        scheduler.start()
        assert(len(c["inners"]) == 4)
        c["results"]['foo'].messages.assert_equal(
            on_next(470, " OOF"),
            on_next(530, "    oOf    "),
            on_completed(570))
        c["results"]['bar'].messages.assert_equal(
            on_next(390, "rab   "),
            on_next(420, "  RAB "),
            on_completed(570))
        c["results"]['baz'].messages.assert_equal(
            on_next(480, "  zab"),
            on_next(510, " ZAb "),
            on_completed(570))
        c["results"]['qux'].messages.assert_equal(
            on_completed(570))
        xs.subscriptions.assert_equal(
            subscribe(200, 570))

    def test_group_by_inner_complete_all(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_completed(570),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))
        inners = {}
        inner_subscriptions = {}
        results = {}
        c = {
            "outer": None,
            "outer_subscription": None,
            "result": None
        }

        def action1(scheduler, state):
            c["outer"] = xs.group_by(
                lambda x: x.lower().strip(),
                lambda x: x[::-1]
            )
            return c["outer"]
        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):
            def on_next(group):
                c["result"] = scheduler.create_observer()
                inners[group.key] = group
                results[group.key] = c["result"]
                inner_subscriptions[group.key] = group.subscribe(c["result"])
            c["outer_subscription"] = c["outer"].subscribe(on_next)
            return c["outer_subscription"]
        scheduler.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            c["outer_subscription"].dispose()
            for sub in inner_subscriptions.values():
                sub.dispose()
        scheduler.schedule_absolute(disposed, action3)

        scheduler.start()
        assert(len(inners) == 4)
        results['foo'].messages.assert_equal(
            on_next(220, "oof  "),
            on_next(240, " OoF "),
            on_next(310, " Oof"),
            on_next(470, " OOF"),
            on_next(530, "    oOf    "),
            on_completed(570))
        results['bar'].messages.assert_equal(
            on_next(270, "  Rab"),
            on_next(390, "rab   "),
            on_next(420, "  RAB "),
            on_completed(570))
        results['baz'].messages.assert_equal(
            on_next(350, "   zaB "),
            on_next(480, "  zab"),
            on_next(510, " ZAb "),
            on_completed(570))
        results['qux'].messages.assert_equal(
            on_next(360, " xuq  "),
            on_completed(570))
        xs.subscriptions.assert_equal(
            subscribe(200, 570))

    def test_group_by_inner_error(self):
        ex = 'ex1'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, "error"),
            on_next(110, "error"),
            on_next(130, "error"),
            on_next(220, "  foo"),
            on_next(240, " FoO "),
            on_next(270, "baR  "),
            on_next(310, "foO "),
            on_next(350, " Baz   "),
            on_next(360, "  qux "),
            on_next(390, "   bar"),
            on_next(420, " BAR  "),
            on_next(470, "FOO "),
            on_next(480, "baz  "),
            on_next(510, " bAZ "),
            on_next(530, "    fOo    "),
            on_error(570, ex),
            on_next(580, "error"),
            on_completed(600),
            on_error(650, 'ex'))
        inner_subscriptions = {}
        inners = {}
        results = {}
        c = {
            "outer_subscription": None,
            "outer": None
        }

        def action1(scheduler, state):
            c["outer"] = xs.group_by(
                lambda x: x.lower().strip(),
                lambda x: x[::-1]
            )
            return c["outer"]
        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):
            def on_next(group):
                result = scheduler.create_observer()
                inners[group.key] = group
                results[group.key] = result

                def action3(scheduler, state):
                    inner_subscriptions[group.key] = group.subscribe(result)

                scheduler.schedule_relative(100, action3)
            c["outer_subscription"] = c["outer"].subscribe(on_next, lambda e: None)
            return c["outer_subscription"]
        scheduler.schedule_absolute(subscribed, action2)

        def action4(scheduler, state):
            c["outer_subscription"].dispose();
            for sub in inner_subscriptions.values():
                sub.dispose()
        scheduler.schedule_absolute(disposed, action4)

        scheduler.start()
        assert(len(inners) == 4)
        results['foo'].messages.assert_equal(
            on_next(470, " OOF"),
            on_next(530, "    oOf    "),
            on_error(570, ex))
        results['bar'].messages.assert_equal(
            on_next(390, "rab   "),
            on_next(420, "  RAB "),
            on_error(570, ex))
        results['baz'].messages.assert_equal(
            on_next(480, "  zab"),
            on_next(510, " ZAb "),
            on_error(570, ex))
        results['qux'].messages.assert_equal(
            on_error(570, ex))
        xs.subscriptions.assert_equal(
            subscribe(200, 570))

    def test_group_by_with_merge(self):
        scheduler = TestScheduler()

        xs = [None]
        results = [None]

        def action1(scheduler, state):
            xs[0] = Observable.from_(["alpha", "apple", "beta", "bat", "gamma"]) \
                              .group_by(lambda s: s[0]) \
                              .map(lambda group: group.to_list()) \
                              .merge_all()
        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):
            results[0] = scheduler.create_observer()
            xs[0].subscribe(results[0])
        scheduler.schedule_absolute(subscribed, action2)

        scheduler.start()

        results[0].messages.assert_equal(
            on_next(200, ["alpha", "apple"]),
            on_next(200, ["beta", "bat"]),
            on_next(200, ["gamma"]),
            on_completed(200))

if __name__ == '__main__':
    unittest.main()
