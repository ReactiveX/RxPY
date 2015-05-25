# Changes

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
- AsyncIOScheduler now works with Python-2.7 and Trollus. Fixes #37
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

## 0.15

- Python slicing and indexing of observables. Thus you can write xs[1:-1:2]
- Aligned backpressure with RxJS
- Renamed all `select()` to `map()` and `where()` to `map()`
- `from_` is now an alias for `from_iterable`. Removed `from_array`
- Fixes for `select_many`/`flat_map`. Selector may return iterable

## 0.14

- Made `ScheduledObserver` thread safe
- Thread safe handling for `take_while` and `group_join`
- Removed dependecy on six (https://pythonhosted.org/six/)
- Added support for IronPython (by removing six)
- Aggregate is now an alias for reduce

## 0.13

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
