# AGENTS.md

This file provides guidance for AI agents (Repo Assist, Copilot, etc.) working in this repository.

## Project Overview

RxPY is [ReactiveX](http://reactivex.io) for Python — a library for composing asynchronous and event-based programs using observable sequences and pipeable operators. It is published to PyPI as the `reactivex` package.

- **Repository**: https://github.com/ReactiveX/RxPY
- **Documentation**: https://rxpy.readthedocs.io/en/latest/
- **Python**: 3.10–3.14

## Repository Layout

```
reactivex/           # Main library package
  abc/               # Abstract base classes (Observable, Observer, Disposable, etc.)
  asyncrx/           # Async/await native reactive extensions (in development)
  disposable/        # Disposable implementations
  internal/          # Internal utilities (not public API)
  observable/        # Observable creation functions (rx.of, rx.from_, etc.)
  observer/          # Observer implementations
  operators/         # Pipeable operators (_map.py, _filter.py, _flat_map.py, etc.)
  scheduler/         # Schedulers (EventLoopScheduler, ThreadPoolScheduler, etc.)
  subject/           # Subject implementations (Subject, BehaviorSubject, etc.)
  testing/           # TestScheduler and related test utilities
  typing.py          # Public type aliases and protocols
tests/               # Test suite (mirrors reactivex/ structure)
examples/            # Usage examples
docs/                # Sphinx documentation source
```

## Development Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run all tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run a specific test file
uv run pytest tests/test_core/

# Type checking
uv run pyright
uv run mypy reactivex

# Linting / formatting
uv run ruff check .
uv run ruff format .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Architecture

### Observable / Observer

The core `Observable[T]` is defined in `reactivex/observable/observable.py`. Observables are cold by default — subscribing triggers execution.

`Observer[T]` carries three callbacks: `on_next`, `on_error`, `on_completed`. Both implement the abstract interfaces in `reactivex/abc/`.

### Operators

Each operator lives in its own file under `reactivex/operators/` (e.g. `_map.py`, `_filter.py`). Every operator is a function that returns a `Callable[[Observable[T]], Observable[U]]` so it can be composed with `pipe()`.

When adding or modifying an operator:
1. Create/edit `reactivex/operators/_<name>.py`
2. Export it from `reactivex/operators/__init__.py`
3. Add tests under `tests/test_observable/` (or the relevant subdirectory)

### Schedulers

Schedulers control concurrency and time. They implement `abc.SchedulerBase`. Tests use `TestScheduler` from `reactivex/testing/` — prefer it over real time in operator tests.

### Typing

The library ships `py.typed` and is fully typed. `reactivex/typing.py` holds public type aliases. Pyright in `strict` mode is the authoritative type checker (see `pyrightconfig` in `pyproject.toml`). Mypy is run as a secondary check.

## Coding Conventions

- Follow existing code style; `ruff` enforces formatting and linting.
- All public functions and classes must have type annotations.
- Operators follow the pattern: top-level function → inner `subscribe` closure → return `Observable(subscribe)`.
- Prefer `rx.pipe()` composition over subclassing.
- No external runtime dependencies beyond `typing-extensions`.

## Testing Conventions

- Use `TestScheduler` for time-based operator tests — do not use `time.sleep`.
- Use `pytest-asyncio` (strict mode) for async tests.
- Tests excluded from ruff/pyright (see `pyproject.toml`) are being migrated — fix them rather than expanding the exclude list.
- Coverage target: maintain or improve existing coverage.

## Labels

When labelling issues and PRs, use:

`bug`, `documentation`, `enhancement`, `help wanted`, `good first issue`, `question`, `duplicate`, `wontfix`, `invalid`, `dependencies`, `operators`, `schedulers`, `subjects`, `asyncio`, `typing`, `examples`, `tests`, `ci`

## Public API Stability

The `reactivex` package follows semantic versioning. Do not rename, remove, or change the signature of any exported symbol without a tracked issue and a major-version bump. Additions and new operators are always welcome.
