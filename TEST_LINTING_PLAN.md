# Multi-Stage Plan: Enable Linting & Type Checking for Tests

## Current Situation

- **184 test files** currently excluded from ruff and pyright
- Tests are excluded in both `pyrightconfig.json` and `pyproject.toml`
- Largest category: **test_observable (142 files)** - 77% of all tests
- Project uses **strict type checking** standards (pyright --strict, mypy --strict)

## Test File Distribution

| Directory | File Count | Percentage |
|-----------|------------|------------|
| test_observable | 142 | 77% |
| test_scheduler | 27 | 15% |
| test_subject | 5 | 3% |
| test_core | 4 | 2% |
| test_disposables | 2 | 1% |
| test_integration | 2 | 1% |
| test_testing | 2 | 1% |
| **Total** | **184** | **100%** |

## Staged Approach

### Stage 0: Format All Test Files (Pre-work) ✅ COMPLETED

**Goal**: Handle all formatting issues upfront before type annotations

**Tasks**:

1. ✅ Run `ruff format tests/` - 19 files reformatted
2. ✅ Updated configuration to use specific directory exclusions
3. ✅ Verified tests still pass after formatting

**Rationale**: Separating formatting from type annotation work makes it easier to review changes and ensures we start from a clean, consistent base.

**Actual Effort**: ~30 minutes

### Stage 1: Infrastructure & Smallest Modules (8 files) ✅ COMPLETED

**Goal**: Validate the approach and establish patterns

**Tasks**:

1. ✅ Updated ruff configuration to match pyright (specific directory exclusions)
2. ✅ Ran `ruff check --fix --unsafe-fixes` - auto-fixed 16 errors
3. ✅ Fixed **test_core/test_priorityqueue.py** - 0 errors
4. ✅ Fixed **test_core/test_observer.py** - 0 errors
5. ✅ Fixed **test_core/test_notification.py** - 0 errors (largest file, most complex)
6. ✅ Fixed **test_disposables/test_disposable.py** - 0 errors (auto-fixed)
7. ✅ Fixed **test_testing/test_marbles.py** - 0 errors
8. ✅ All 75 Stage 1 tests pass

**Patterns Discovered**:

- Add `-> None` return types to all test functions
- Use explicit type parameters for generics (e.g., `OnError[int]`, `OnCompleted[int]`)
- Convert string exceptions to `Exception("message")` objects
- Use `cast()` with documented justifications for test patterns that go beyond public API
- Replace `== None` with `is not None` or `is None`
- Add type annotations to all observer classes and helper functions

**Rationale**: These are likely the simplest and will help identify common patterns and issues.

**Actual Effort**: ~3 hours

### Stage 2: Medium Modules (9 files) ⚠️ PARTIAL - test_integration COMPLETE

**Goal**: Build confidence with isolated modules

**Status**: test_integration complete, test_subject deferred to preserve commit checkpoint

**Tasks**:

1. ⏳ Fix **test_subject** (5 files) - Deferred (requires ~2000 lines of fixes)
2. ✅ Fix **test_integration** (2 files) - COMPLETE
   - ✅ **test_integration/test_concat_repeat.py** - 0 errors
   - ✅ **test_integration/test_group_reduce.py** - 0 errors
   - ✅ All 3 integration tests pass
3. ✅ Excluded test_subject from pyproject.toml for pre-commit checkpoint
4. ✅ Verified all enabled tests pass (78 tests total)

**Additional Patterns Discovered**:

- Marble testing requires `None, None` parameters for value_lookup and error_lookup
- Complex operator chains (group_by, flat_map): Extract helper function with explicit `Callable[[Observable[Any]], Observable[Any]]` type
- Integration tests validate runtime behavior, so `Any` types with documented justification are acceptable
- GroupedObservable type inference issues: Use helper functions instead of inline lambdas

**Rationale**: Still manageable size, builds confidence before tackling large modules. Split to allow checkpoint commit.

**Actual Effort**: ~1 hour (test_integration only)

### Stage 3: Scheduler Module (27 files)

**Goal**: Tackle a substantial module with known complexity

**Tasks**:
Fix **test_scheduler** (27 files) - May need to be sub-batched:

- test_scheduler/test_eventloop (AsyncIO schedulers)
- test_scheduler/test_currentthread
- test_scheduler/test_historicalscheduler
- test_scheduler/test_timeout
- Other scheduler tests

**Rationale**: Isolated module with clear boundaries, but large enough to benefit from batching.

**Estimated Effort**: ~3-5 hours

### Stage 4: Observable Module - Batched (142 files)

**Goal**: Systematically fix the largest test suite by operator category

The massive observable tests need careful batching by operator category to align with the mixin architecture:

#### Batch 4a: Filtering Operators (~20 files)

- filter, take, skip, take_while, skip_while
- distinct, distinct_until_changed
- element_at, first, last, sample, throttle

**Estimated Effort**: ~2-3 hours

#### Batch 4b: Transformation Operators (~25 files)

- map, flat_map, flat_map_indexed, flat_map_latest
- scan, reduce, expand
- pluck, starmap, switch_map

**Estimated Effort**: ~3-4 hours

#### Batch 4c: Combination Operators (~20 files)

- merge, concat, zip, zip_with_iterable
- combine_latest, with_latest_from
- start_with, concat_all, merge_all

**Estimated Effort**: ~2-3 hours

#### Batch 4d: Time-Based Operators (~15 files)

- debounce, throttle, sample, delay
- timeout, interval, timer
- timestamp, time_interval

**Estimated Effort**: ~2-3 hours

#### Batch 4e: Mathematical Operators (~10 files)

- count, sum, average, min, max
- reduce (if not covered in 4b)

**Estimated Effort**: ~1-2 hours

#### Batch 4f: Error Handling Operators (~10 files)

- catch, retry, on_error_resume_next
- catch_with_iterable

**Estimated Effort**: ~1-2 hours

#### Batch 4g: Utility Operators (~15 files)

- do_action, do, tap
- materialize, dematerialize
- observe_on, subscribe_on
- timestamp, timeout

**Estimated Effort**: ~2-3 hours

#### Batch 4h: Windowing Operators (~12 files)

- buffer, buffer_with_count, buffer_with_time
- window, window_with_count, window_with_time
- group_by, partition

**Estimated Effort**: ~2-3 hours

#### Batch 4i: Remaining Operators (~15 files)

- All other observable tests not covered above
- share, publish, replay, ref_count
- to_list, to_dict, to_set
- contains, sequence_equal, default_if_empty

**Estimated Effort**: ~2-3 hours

## Configuration Strategy

**All configuration is consolidated in `pyproject.toml`** - no separate pyright config file needed.

### pyproject.toml

Use granular exclude patterns that get removed as files are fixed:

```toml
[tool.ruff]
line-length = 88
target-version = "py310"
exclude = [
    ".git",
    "__pycache__",
    "docs/source/conf.py",
    "old",
    "build",
    "dist",
    "notebooks",
    "examples",
    # Stage 1-3: Remove these directory exclusions as fixed
    "tests/test_core",
    "tests/test_disposables",
    "tests/test_testing",
    "tests/test_subject",
    "tests/test_integration",
    "tests/test_scheduler",
    # Stage 4: For test_observable, exclude individual files
    # Remove files from this list as batches are completed
    "tests/test_observable/test_filter.py",
    "tests/test_observable/test_map.py",
    # ... etc (add all 142 files, remove as fixed)
]

[tool.pyright]
include = ["reactivex", "tests"]
exclude = [
    # Stage 1-3: Remove these directory exclusions as fixed
    "tests/test_core",
    "tests/test_disposables",
    "tests/test_testing",
    "tests/test_subject",
    "tests/test_integration",
    "tests/test_scheduler",
    # Stage 4: For test_observable, exclude individual files
    # Remove files from this list as batches are completed
    "tests/test_observable/test_filter.py",
    "tests/test_observable/test_map.py",
    # ... etc (add all 142 files, remove as fixed)
]
reportImportCycles = false
reportMissingImports = false
pythonVersion = "3.10"
typeCheckingMode = "strict"
```

## Common Issues to Address Per Batch

1. **Missing type annotations** on test methods and fixtures
   - Add return types to test methods (`-> None`)
   - Type test helper functions
   - Type lambda parameters

2. **Any types** from operators without proper casts
   - Use documented `cast` with justifications
   - Preserve type parameters through operator chains

3. **Untyped test helpers** and utility functions
   - Create typed wrappers or add annotations
   - Use generics where appropriate

4. **Import organization** (isort/ruff formatting)
   - Ensure imports are sorted correctly
   - Group imports properly (stdlib, third-party, first-party)

5. **TestScheduler type safety** - Often uses `Any` for message values
   - Use proper type parameters for `ReactiveTest.on_next(time, value)`
   - Consider `Observable[Any]` where message types vary

6. **Observer/Observable type parameters** - Need explicit type vars
   - Ensure `Observable[T]` is properly typed throughout tests
   - Use `TypeVar` for generic test helpers

7. **Deprecated APIs** - Update any deprecated datetime usage
   - Replace `datetime.utcfromtimestamp()` with timezone-aware versions
   - Use `default_now()` where appropriate

8. **Test class inheritance**
   - Ensure `unittest.TestCase` inheritance is properly typed
   - Type `setUp` and `tearDown` methods

## Safety Measures

- ✅ Run full test suite after each stage (`uv run pytest`)
- ✅ Keep changes focused on type annotations and linting fixes only
- ✅ Don't change test logic or behavior
- ✅ Use documented `cast` with justifications when needed
- ✅ Run pre-commit hooks before committing (`uv run pre-commit run --all-files`)
- ✅ Commit after each successful batch with clear commit messages
- ✅ Verify pyright and ruff pass on modified files before proceeding

## Progress Tracking

- [x] Stage 0: Format All Test Files (Pre-work) ✅
  - [x] Run `ruff format tests/` (19 files reformatted)
  - [x] Review and commit formatting changes (commit: 73495f83)
  - [x] Verify tests still pass
  - [x] Update ruff config to use specific directory exclusions (commit: ecf450ee)

  **Note**: Formatting worked even with blanket "tests" exclusion because explicitly passing paths to ruff overrides excludes by default.

- [x] Stage 1: Infrastructure & Smallest Modules (8 files) ✅
  - [x] Update configuration files
  - [x] Fix test_core (4 files) - 0 errors
  - [x] Fix test_disposables (2 files) - 0 errors
  - [x] Fix test_testing (2 files) - 0 errors
  - [x] Document patterns
  - [x] All 75 tests pass

- [x] Stage 2: Medium Modules (9 files) ⚠️ PARTIAL
  - [ ] Fix test_subject (5 files) - Deferred
  - [x] Fix test_integration (2 files) - 0 errors, 3 tests pass
  - [x] Exclude test_subject from pyproject.toml
  - [x] Run enabled tests (78 tests total)

- [ ] Stage 3: Scheduler Module (27 files)
  - [ ] Fix test_scheduler files
  - [ ] Run full test suite

- [ ] Stage 4: Observable Module (142 files)
  - [ ] Batch 4a: Filtering operators (~20 files)
  - [ ] Batch 4b: Transformation operators (~25 files)
  - [ ] Batch 4c: Combination operators (~20 files)
  - [ ] Batch 4d: Time-based operators (~15 files)
  - [ ] Batch 4e: Mathematical operators (~10 files)
  - [ ] Batch 4f: Error handling operators (~10 files)
  - [ ] Batch 4g: Utility operators (~15 files)
  - [ ] Batch 4h: Windowing operators (~12 files)
  - [ ] Batch 4i: Remaining operators (~15 files)

- [ ] Final: Complete cleanup
  - [ ] Remove all test exclusions from config files
  - [ ] Create TESTING_TYPES.md documentation
  - [ ] Update CLAUDE.md with testing type patterns
  - [ ] Final full test suite run
  - [ ] Final pre-commit check

## Pattern Documentation

As patterns emerge during Stage 1, document them here or in a separate `TESTING_TYPES.md` file:

### Common Pattern 1: Type Test Methods

```python
def test_something(self) -> None:
    """Test description."""
    # Test implementation
```

### Common Pattern 2: Typed TestScheduler Usage

```python
def test_operator(self) -> None:
    scheduler = TestScheduler()

    xs: Observable[int] = scheduler.create_hot_observable(
        ReactiveTest.on_next(210, 1),
        ReactiveTest.on_next(220, 2),
        ReactiveTest.on_completed(250)
    )

    result = scheduler.start(lambda: xs.pipe(ops.map(lambda x: x * 2)))
```

### Common Pattern 3: Cast for Complex Operators

```python
from collections.abc import Callable
from typing import Any, cast

def test_complex_operator(self) -> None:
    source: Observable[int] = # ...

    # When operator type inference fails
    op: Callable[[Observable[int]], Observable[str]] = cast(
        "Callable[[Observable[int]], Observable[str]]",
        ops.map(lambda x: str(x))
        # Cast is safe because map preserves the transformation type
    )
    result = source.pipe(op)
```

## Estimated Total Effort

- **Stage 0**: ~15-30 minutes (formatting)
- **Stage 1**: ~2-4 hours (includes setup and pattern discovery)
- **Stage 2**: ~1-2 hours
- **Stage 3**: ~3-5 hours
- **Stage 4**: ~15-25 hours (across 9 batches)
- **Final cleanup**: ~1-2 hours
- **Total**: ~22.5-38.5 hours

## Success Criteria

1. ✅ All test files pass `pyright --strict` with zero errors/warnings
2. ✅ All test files pass `ruff check` with zero errors
3. ✅ All test files pass `ruff format --check` (properly formatted)
4. ✅ Full test suite passes (`uv run pytest`)
5. ✅ Pre-commit hooks pass on all test files
6. ✅ No `type: ignore` comments (use documented `cast` instead)
7. ✅ Comprehensive pattern documentation exists for future test development

## Notes

- This plan aligns with RxPY's strict type safety standards
- Breaking work into small batches allows for incremental progress
- Each stage can be completed and committed independently
- If a batch proves too large, it can be further subdivided
- Pattern documentation will help maintain type safety in future tests
