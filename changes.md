# Changes

## 1.0.0rc3

- Removed some non git files files that were added to the package by accident
- Added `Observable#to_iterable()`

## 1.0.0rc2

- Fixed examples. Use `debounce` instead of `throttle`
- Fixed wrong aliases for `select_switch`.

## 1.0.0rc1

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
- Renamed `throttle()` to `debounce()` and added `throttle_with_timeout()` as alias
- Renamed `any()` to `some()`
- Simplified `sequence_equal()`
- Bugfix for `take()` when no count given
- Removed internal operator `final_value()` which did exactly the same as `last()`
- Added `to_iterable()` as alias to `to_list()`
- Added `throttle_first()`
