import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestDo(unittest.TestCase):
    def test_do_should_see_all_values(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
        i = [0]
        sum = [2 + 3 + 4 + 5]

        def create():
            def action(x):
                i[0] += 1
                sum[0] -= x
                return sum[0]
            return xs.do_action(action)

        scheduler.start(create)

        self.assertEqual(4, i[0])
        self.assertEqual(0, sum[0])

    def test_do_plain_action(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
        i = [0]

        def create():
            def action(x):
                i[0] += 1
                return i[0]
            return xs.do_action(action)
        scheduler.start(create)

        self.assertEqual(4, i[0])

    def test_do_next_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
        i = [0]
        sum = [2 + 3 + 4 + 5]
        completed = [False]
        def create():
            def on_next(x):
                i[0] += 1
                sum[0] -= x
            def on_completed():
                completed[0] = True
            return xs.do_action(on_next=on_next, on_completed=on_completed)

        scheduler.start(create)

        self.assertEqual(4, i[0])
        self.assertEqual(0, sum[0])
        assert(completed[0])

    def test_do_next_completed_never(self):
        scheduler = TestScheduler()
        i = [0]
        completed = [False]

        def create():
            def on_next(x):
                i[0] += 1
            def on_completed():
                completed = True
            return Observable.never().do_action(on_next=on_next, on_completed=on_completed)

        scheduler.start(create)

        self.assertEqual(0, i[0])
        assert(not completed[0])

    def test_do_action_without_next(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2),  on_completed(250))
        completed = [False]
        def create():
            def on_completed():
                completed[0] = True
            return xs.do_action(on_completed=on_completed)

        scheduler.start(create)

        assert(completed[0])

# def test_do_next_error(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     scheduler.start(create)
#         return xs.do_action(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = e == ex


#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(saw_error)

# def test_do_next_error_not(self):
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     scheduler.start(create)
#         return xs.do_action(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = True


#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(not saw_error)

# def test_do_next_error_completed(self):
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     has_completed = False
#     scheduler.start(create)
#         return xs.do_action(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = True
#         }, function () {
#             has_completed = True


#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(not saw_error)
#     assert(has_completed)

# def test_do_next_error_completed_error(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     has_completed = False
#     scheduler.start(create)
#         return xs.do_action(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = ex == e
#         }, function () {
#             has_completed = True


#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(saw_error)
#     assert(not has_completed)

# def test_do_next_error_completed_never(self):
#     scheduler = TestScheduler()
#     i = [0]
#     saw_error = False
#     has_completed = False
#     scheduler.start(create)
#         return Observable.never().do_action(function (x) {
#             i[0] += 1
#         }, function (e) {
#             saw_error = True
#         }, function () {
#             has_completed = True

#     self.assertEqual(0, i)
#     assert(not saw_error)
#     assert(not has_completed)

# def test_Do_Observer_SomeDataWithError(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     has_completed = False
#     scheduler.start(create)
#         return xs.do_action(Observer.create(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = e == ex
#         }, function () {
#             has_completed = True
#         }))

#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(saw_error)
#     assert(not has_completed)

# def test_do_observer_some_data_with_error(self):
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = [0]
#     sum = [2 + 3 + 4 + 5]
#     saw_error = False
#     has_completed = False
#     scheduler.start(create)
#         return xs.do_action(Observer.create(function (x) {
#             i[0] += 1
#             sum -= x
#         }, function (e) {
#             saw_error = True
#         }, function () {
#             has_completed = True
#         }))

#     self.assertEqual(4, i)
#     self.assertEqual(0, sum)
#     assert(not saw_error)
#     assert(has_completed)

# def test_do1422_next_next_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () {
#             raise Exception(ex)


#     results.messages.assert_equal(on_error(210, ex))

# def test_do1422_next_completed_next_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () {
#             throw ex
#         }, _undefined, function () {

#     results.messages.assert_equal(on_error(210, ex))

# def test_do1422_next_completed_completed_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () { }, _undefined, function () {
#             throw ex


#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))

# def test_do1422_next_error_next_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () {
#             raise Exception(ex)
#         }, function () {

#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_NextError_NextThrows(self):
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.do_action(function () { }, function () {
#             raise Exception(ex)2


#     results.messages.assert_equal(on_error(210, ex2))

# def test_Do1422_NextErrorCompleted_NextThrows(self):
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () {
#             raise Exception(ex)
#         }, function () { }, function () {

#     results.messages.assert_equal(on_error(210, ex))

# def test_do1422_next_error_completed_error_throws(self):
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.do_action(function () { }, function () {
#             raise Exception(ex)2
#         }, function () {

#     results.messages.assert_equal(on_error(210, ex2))

# def test_do1422_next_error_completed_completed_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(function () { }, function () { }, function () {
#             raise Exception(ex)


#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))

# def test_do1422_observer_next_throws(self):
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(Observer.create(function () {
#             raise Exception(ex)
#         }, function () { }, function () { }))

#     results.messages.assert_equal(on_error(210, ex))

# def test_do1422_observer_error_throws(self):
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.do_action(Observer.create(function () { }, function () {
#             raise Exception(ex)2
#         }, function () { }))

#     results.messages.assert_equal(on_error(210, ex2))

# def test_do1422_observer_completed_throws(self):
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.do_action(Observer.create(function () { }, function () { }, function () {
#             raise Exception(ex)
#         }))

#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))
