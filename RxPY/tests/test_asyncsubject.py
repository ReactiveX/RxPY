from rx import Observable, Observer
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable
from rx.subjects import BehaviorSubject

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

def test_infinite():
    var results1, results2, results3, scheduler, subject, subscription, subscription1, subscription2, subscription3, xs
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_next(630, 8),
        on_next(710, 9),
        on_next(870, 10),
        on_next(940, 11),
        on_next(1020, 12)
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()
    scheduler.schedule_absolute(100, function () {
        subject = AsyncSubject()
    scheduler.schedule_absolute(200, function () {
        subscription = xs.subscribe(subject)
    scheduler.schedule_absolute(1000, function () {
        subscription.dispose()
    scheduler.schedule_absolute(300, function () {
        subscription1 = subject.subscribe(results1)
    scheduler.schedule_absolute(400, function () {
        subscription2 = subject.subscribe(results2)
    scheduler.schedule_absolute(900, function () {
        subscription3 = subject.subscribe(results3)
    scheduler.schedule_absolute(600, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(700, function () {
        subscription2.dispose()
    scheduler.schedule_absolute(800, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(950, function () {
        subscription3.dispose()
    scheduler.start()
    results1.messages.assertEqual()
    results2.messages.assertEqual()
    results3.messages.assertEqual()

def test_Finite():
    var results1, results2, results3, scheduler, subject, subscription, subscription1, subscription2, subscription3, xs
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_completed(630),
        on_next(640, 9),
        on_completed(650),
        on_error(660, 'ex')
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()
    scheduler.schedule_absolute(100, function () {
        subject = AsyncSubject()
    scheduler.schedule_absolute(200, function () {
        subscription = xs.subscribe(subject)
    scheduler.schedule_absolute(1000, function () {
        subscription.dispose()
    scheduler.schedule_absolute(300, function () {
        subscription1 = subject.subscribe(results1)
    scheduler.schedule_absolute(400, function () {
        subscription2 = subject.subscribe(results2)
    scheduler.schedule_absolute(900, function () {
        subscription3 = subject.subscribe(results3)
    scheduler.schedule_absolute(600, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(700, function () {
        subscription2.dispose()
    scheduler.schedule_absolute(800, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(950, function () {
        subscription3.dispose()
    scheduler.start()
    results1.messages.assertEqual()
    results2.messages.assertEqual(on_next(630, 7), on_completed(630))
    results3.messages.assertEqual(on_next(900, 7), on_completed(900))

def test_error():
    var ex, results1, results2, results3, scheduler, subject, subscription, subscription1, subscription2, subscription3, xs
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_next(70, 1),
        on_next(110, 2),
        on_next(220, 3),
        on_next(270, 4),
        on_next(340, 5),
        on_next(410, 6),
        on_next(520, 7),
        on_error(630, ex),
        on_next(640, 9),
        on_completed(650),
        on_error(660, 'ex2')
    )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()
    scheduler.schedule_absolute(100, function () {
        subject = AsyncSubject()
    scheduler.schedule_absolute(200, function () {
        subscription = xs.subscribe(subject)
    scheduler.schedule_absolute(1000, function () {
        subscription.dispose()
    scheduler.schedule_absolute(300, function () {
        subscription1 = subject.subscribe(results1)
    scheduler.schedule_absolute(400, function () {
        subscription2 = subject.subscribe(results2)
    scheduler.schedule_absolute(900, function () {
        subscription3 = subject.subscribe(results3)
    scheduler.schedule_absolute(600, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(700, function () {
        subscription2.dispose()
    scheduler.schedule_absolute(800, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(950, function () {
        subscription3.dispose()
    scheduler.start()
    results1.messages.assertEqual()
    results2.messages.assertEqual(on_error(630, ex))
    results3.messages.assertEqual(on_error(900, ex))

def test_canceled():
    var results1, results2, results3, scheduler, subject, subscription, subscription1, subscription2, subscription3, xs
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(
        on_completed(630),
        on_next(640, 9),
        on_completed(650),
        on_error(660, 'ex')
        )
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()
    scheduler.schedule_absolute(100, function () {
        subject = AsyncSubject()
    scheduler.schedule_absolute(200, function () {
        subscription = xs.subscribe(subject)
    scheduler.schedule_absolute(1000, function () {
        subscription.dispose()
    scheduler.schedule_absolute(300, function () {
        subscription1 = subject.subscribe(results1)
    scheduler.schedule_absolute(400, function () {
        subscription2 = subject.subscribe(results2)
    scheduler.schedule_absolute(900, function () {
        subscription3 = subject.subscribe(results3)
    scheduler.schedule_absolute(600, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(700, function () {
        subscription2.dispose()
    scheduler.schedule_absolute(800, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(950, function () {
        subscription3.dispose()
    scheduler.start()
    results1.messages.assertEqual()
    results2.messages.assertEqual(on_completed(630))
    results3.messages.assertEqual(on_completed(900))

def test_subject_disposed():
    var results1, results2, results3, scheduler, subject, subscription1, subscription2, subscription3
    scheduler = TestScheduler()
    results1 = scheduler.create_observer()
    results2 = scheduler.create_observer()
    results3 = scheduler.create_observer()
    scheduler.schedule_absolute(100, function () {
        subject = AsyncSubject()
    scheduler.schedule_absolute(200, function () {
        subscription1 = subject.subscribe(results1)
    scheduler.schedule_absolute(300, function () {
        subscription2 = subject.subscribe(results2)
    scheduler.schedule_absolute(400, function () {
        subscription3 = subject.subscribe(results3)
    scheduler.schedule_absolute(500, function () {
        subscription1.dispose()
    scheduler.schedule_absolute(600, function () {
        subject.dispose()
    scheduler.schedule_absolute(700, function () {
        subscription2.dispose()
    scheduler.schedule_absolute(800, function () {
        subscription3.dispose()
    scheduler.schedule_absolute(150, function () {
        subject.on_next(1)
    scheduler.schedule_absolute(250, function () {
        subject.on_next(2)
    scheduler.schedule_absolute(350, function () {
        subject.on_next(3)
    scheduler.schedule_absolute(450, function () {
        subject.on_next(4)
    scheduler.schedule_absolute(550, function () {
        subject.on_next(5)
    scheduler.schedule_absolute(650, function () {
        raises(function () {
            subject.on_next(6)
   
    scheduler.schedule_absolute(750, function () {
        raises(function () {
            subject.on_completed()
   
    scheduler.schedule_absolute(850, function () {
        raises(function () {
            subject.on_error('ex')
   
    scheduler.schedule_absolute(950, function () {
        raises(function () {
            subject.subscribe()
   
    scheduler.start()
    results1.messages.assertEqual()
    results2.messages.assertEqual()
    results3.messages.assertEqual()
