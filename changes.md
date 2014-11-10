# Changes

## 0.13

- Aligning throttle type operator naming with RxJS and RxJava
- Added `throttle_last()` as alias for `sample()`
- Renamed `throttle()` to `debounce()` and added `throttle_with_timeout()` as alias
- Renamed `any()` to `some()`
- Simplified `sequence_equal()`
- Bugfix for `take()` when no count given
- Removed internal operator `final_value()` which did exactly the same as `last()`