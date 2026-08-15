default: check

# Create or refresh the uv-managed development environment.
install:
    uv sync

# Run the test suite; pass pytest arguments after `--`.
test *args:
    uv run pytest {{args}}

# Run the same formatting, linting, and type checks as CI.
lint:
    uv run pre-commit run --all-files --show-diff-on-failure

# Run both configured type checkers directly.
typecheck:
    uv run pyright
    uv run mypy reactivex

# Apply Ruff's safe lint fixes and formatter.
format:
    uv run ruff check --fix .
    uv run ruff format .

# Run all checks required before opening a pull request.
check: lint test

# Build source and wheel distributions without local uv sources.
build:
    uv build --no-sources

# Refresh all versions allowed by pyproject.toml.
update:
    uv lock --upgrade
    uv sync

# Validate the lockfile without modifying it.
lock-check:
    uv lock --check
