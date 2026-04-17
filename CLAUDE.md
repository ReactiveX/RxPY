# CLAUDE.md

See [AGENTS.md](AGENTS.md) for full project guidance — build commands, architecture, conventions, and testing.

## Quick Reference

```bash
uv sync                   # install deps
uv run pytest             # run tests
uv run pytest -n auto     # run tests in parallel
uv run pyright            # type check (authoritative)
uv run ruff check .       # lint
uv run ruff format .      # format
```
