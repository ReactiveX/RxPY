---
last_commit_released: 2975deb528c9eec73c76cf8bb53fc8780f31de45
pre_release: rc
name: reactivex
updaters:
  - command: ./scripts/shipit_bump_version.sh {version}
---

# Changelog

All notable changes to this project will be documented in this file. Starting
with version 5.0.0-rc.1, entries are generated automatically by
[EasyBuild.ShipIt](https://github.com/easybuild-org/EasyBuild.ShipIt) from
conventional-commit messages.

PyPI uses PEP 440 (`5.0.0rc1`), while ShipIt records SemVer (`5.0.0-rc.1`) in
this file; the release script normalizes between them.

## 5.0.0-rc.1 - 2026-04-20

<strong><small>[View changes on Github](https://github.com/ReactiveX/RxPY/compare/8b59bc7394f1b6a8a78e2fc4b5efe200d4f47f89..2975deb528c9eec73c76cf8bb53fc8780f31de45)</small></strong>

- Typing: Added `Action` and `StartableFactory` to `reactivex.typing.__all__`,
  making them part of the explicit public API surface.
- Docs: Added missing docstring to `on_error_resume_next` operator.
- Operators: Fixed scheduler forwarding in `pairwise`, `to_marbles`, and
  `delay_with_mapper` (subscription-delay path). These operators now pass the
  `scheduler` argument through to `source.subscribe(...)` and, in the case of
  `delay_with_mapper`, to the subscription-delay observable, consistent with
  all other pipeable operators. Closes #480 (partial — the operators listed
  in the issue that were not yet fixed).
- CI: Skip `tests/test_scheduler/test_mainloop/test_tkinterscheduler.py` on
  PyPy (all platforms). The module creates a Tk root at import time; PyPy's
  `_tkinter` finalizer calls `threading.notify_all` during interpreter
  shutdown and aborts the xdist worker, failing whichever unrelated test
  was running. Previously guarded only on macOS+PyPy.
- Fix: `reactivex.timer(duetime, period)` now correctly resets the initial
  delay on each resubscription (e.g. via `repeat()`). Previously `nonlocal
  duetime` in the subscribe closure mutated the shared outer variable so
  subsequent subscriptions would use the stale absolute time computed by the
  first subscription, causing the timer to fire immediately instead of waiting
  for `duetime`. Fixes #697.
- Testing: Fixed pyright strict-mode type errors in `tests/test_subject/` (added type
  annotations to closure containers, callback function parameters, and narrowed `None`
  checks). Removed `tests/test_subject/` from the pyright exclude list.
- Testing: Fixed ruff lint issues in `tests/test_scheduler/` (import ordering,
  f-string upgrades, `object` base class removal) and removed it from the
  ruff exclude list. `tests/test_subject/` also removed from the ruff exclude
  list as it already passed all checks.
- Testing: Fixed pyright (standard-mode) type errors in `tests/test_scheduler/`:
  corrected `@classmethod` overrides of `VirtualTimeScheduler.add`,
  fixed `[None]`-typed list variables, updated optional-import suppression
  comments (`# type: ignore[import-untyped]`), narrowed callback parameter
  types, and aligned `ScheduledItemTestScheduler` method signatures with the
  `Scheduler` base class.
- CI: Standardised `actions/setup-python` to `@v5` across all workflow jobs.

## 5.0.0-alpha.2

- Documentation header formatting fixes.

## 5.0.0-alpha.1

- **Fluent method chaining** — operators are now available as methods on
  `Observable` in addition to the existing `pipe()` style. Both work
  interchangeably and can be mixed freely. Implemented via eleven category
  mixins (transformation, filtering, combination, error handling,
  windowing/buffering, multicasting, etc.). Zero breaking changes from 4.x —
  all existing `pipe()`-based code continues to work. (#743)
- Migrated project tooling from Poetry to `uv`.
- Replaced Black + isort with Ruff for formatting and linting.
- Dropped Python 3.8; added support for Python 3.11, 3.12, 3.13.
- Added `scheduler` parameter to `run()` for consistent scheduling control.
- Fixed `subscribe_on` not forwarding scheduler to the source. Thanks to
  @MainRo
- Minor internal: renamed `ReplaySubject.window` to `ReplaySubject._window`
  to free the `window` name for the new method.

## 4.0.0

- Renamed the distribution from `rx` to `reactivex` (`pip install reactivex`).
- Flattened the package: `Observable` and operators now live at the top level
  (`rx.core` gone).
- Raised minimum Python to 3.7.
- Full pyright-strict type coverage; `disallow_untyped_defs` enforced.
- Migrated from `setup.py` to Poetry.
- Improved scheduler type annotations and asyncio thread-safety.
- Internal operators renamed with a leading underscore (`_map`, `_filter`,
  etc.).
- Marble-diagram documentation added for every operator.
- Test scheduler and marble-testing improvements. Thanks to @MainRo

## 3.0.0

- Replaced method chaining with a pipe-based functional API as the
  recommended style.
- Dropped Python 2 support; Python 3.6+ only.
- Renamed the `concurrency` package to `scheduler`; split mainloop and
  eventloop schedulers into their own modules.
- Simplified variadic operator signatures (`amb`, `combine_latest`, `concat`,
  `merge`, `on_error_resume_next`, `catch`, `zip`) — the leading `Iterable`
  argument is gone.
- Removed `result_mapper` from `join`, `group_join`, `zip`, `generate`.
- Added comprehensive type hints and a `py.typed` marker (PEP 561).
- Collapsed `AnonymousObservable` into `Observable`.
- Renamed `catch_exception` to `catch`.
- Added `TrampolineScheduler` and priority-queue scheduler improvements.
- Replaced the blocking observable with a single `run()` function.

## 2.0.0-alpha

- Extension methods and extension class methods have been removed. This
  makes it much easier for editors and IDEs to validate the code and
  perform code completion.
- Python 3.6+ only with type hints
- Google docstring style.

## 1.5.0

- Refactored virtual time scheduling. Fixes #95. Thanks to @djarb
- Fixed Visual Studio project files and moved to ide folder.
- Remove timer operations from base `SchedulerBase` class.
- Scheduler.now is now a property to align with Rx.NET
- Bugfix for periodic scheduling. Fixes #91. Thanks to @frederikaalund
- Demonize all threads in `TimeoutScheduler`. Fixes #90
- Enable subscription with duck-typed observer.
- Added new core module. Observable, Observer, Scheduler and Disposable
  are now ABCs.
- Synced backpressure with RxJS to fix #87
- Do not overwrite scheduler keyword arg. Fixes #85. Thanks to @rjayatilleka
- Added async iterator example.
- Added support for awaiting observables
- Fixed issue #83 with `int + datetime.datetime` in timer.py. Thanks to @AlexMost

## 1.2.6

- Fixes for TwistedScheduler raising AlreadyCalled error #78. Thanks to
  @mchen402 and @jcwilson.
- Use CurrentThreadScheduler as default for just/return_value. Fixes #76

## 1.2.5

- Added wxscheduler.py for use with wxPython applications thanks to
  @bosonogi
- Added eventletscheduler.py for use with Eventlet thanks to @jalandip
- Protect generators that are not thread safe. Fixes #71

## 1.2.4

- Threads are now daemonic by default. Thus they will exit if parent
  thread exits which should probably be what most people want.
- Fix for recursive scheduling, thanks to @smeder
- Fix for NewThreadScheduler. Now uses EventLoopScheduler to make sure
  scheduled actions by scheduled actions happens on the same thread.
- Uses shields.io to uniformize and fix the badges, thanks to @DavidJFelix

## 1.2.3

- Fix optional parameter in `delay_subscription`. Thanks to @angelsanz.
- Simplified `adapt_call` in `util.py` which makes higher order functions
  accept more forms of callables.
- Fix for Python 2.7 in `timeflies_qt.py`.

## 1.2.2

- Added Qt mainloop scheduler thanks to @jdreaver.
- Bugfix, wse `threading.RLock` instead of `threading.Lock` since
  `BehaviorSubject` may share lock with "child" operator at subscribe
  time. Fixes #50

## 1.2.1

- Fix to preserve the original error message for exceptions #44, thanks
  to @hangtwenty
- Fixed bug in `combine_latest()`. Fixes #48.
- Added `to_marbles()` and `from_marbles()`. Available from module
  `rx.testing.marbles`.
- Added [Getting Started](https://github.com/ReactiveX/RxPY/blob/master/notebooks/Getting%20Started.ipynb)
  IPython Notebook.
- Added `share()` as alias for `publish().ref_count()`.
- Added error handling example at https://github.com/ReactiveX/RxPY/blob/master/examples/errors/failing.py

## 1.2.0

- Removed impl. of `merge_observable` and made it an alias of `merge_all`
- Bugfix for #40. Every subscription needs it's own iterator in `from_()`.
  Thanks to @hangtwenty.
- Bugfix in `from_string()` debug method.
- Added `TkInterScheduler.schedule_periodic()` thanks to @pillmuncher. #39
- Bugfix for #35. Refactored `zip_array` to use `zip` instead.
- AsyncIOScheduler now works with Python-2.7 and Trollius. Fixes #37
  thanks to @hangtwenty.
- Added `with_latest_from` extension method #34. Thanks to @pillmuncher.

## 1.1.0

- Transducers via `Observable.transduce()`
- `adapt_call` no longer requires the inspect module
- Support callable instance, instance method, and class method for `adapt_call`
  thanks to @succhiello.
- Added example using concurrent futures for compute-intensive task
  parallelization, thanks to @38elements.
- Got chess example working again under Python 2.7 thansks to @enobayram.
- Added example for async generator.
- Many PEP 8 fixes.

## 1.0.0

- Fixed bug in ScheduledDisposable#dispose. Only dispose if not disposed
- Fixed typo in `Pattern#_and`. Should be `Pattern#and_`
- Fixed bug. Replaced push with append  in controlledsubject.py
- Refeactored `observer_from_notifier` to `Observer.from_notification`
- Added missing rx.linq.observable.blocking from setup.py
- Added missing rx.joins from setup.py
- Removed some non git files files that were added to the package by accident
- Added `Observable#to_iterable()`
- Fixed examples. Use `debounce` instead of `throttle`
- Fixed wrong aliases for `select_switch`.
- Added join patterns. `Observable.when` and `Observable#and_`
- Added `BlockingObservable`and operators `for_each` and `to_iterable`
- Started adding docstrings as reStructuredText in order for PyCharm to infer
  types. Operators will eventually be converted to new syntax
- Refactored operators to use C# like extensionmethods using function decorators
- More PEP8 alignment

## 0.15.0

- Python slicing and indexing of observables. Thus you can write xs[1:-1:2]
- Aligned backpressure with RxJS
- Renamed all `select()` to `map()` and `where()` to `map()`
- `from_` is now an alias for `from_iterable`. Removed `from_array`
- Fixes for `flat_map`/`flat_map`. Selector may return iterable

## 0.14.0

- Made `ScheduledObserver` thread safe
- Thread safe handling for `take_while` and `group_join`
- Removed dependecy on six (https://pythonhosted.org/six/)
- Added support for IronPython (by removing six)
- Aggregate is now an alias for reduce

## 0.13.0

- Aligning throttle type operator naming with RxJS and RxJava
- Added `throttle_last()` as alias for `sample()`
- Renamed `throttle()` to `debounce()` and added `throttle_with_timeout()` as
  alias
- Renamed `any()` to `some()`
- Simplified `sequence_equal()`
- Bugfix for `take()` when no count given
- Removed internal operator `final_value()` which did exactly the same as
  `last()`
- Added `to_iterable()` as alias to `to_list()`
- Added `throttle_first()`
