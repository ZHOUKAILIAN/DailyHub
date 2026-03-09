# Repository Guidelines

## Project Structure & Module Organization
- `checkin/xiaojuchongdian/src/`: runnable Xiaoju task code (`main.py` CLI entrypoint, `router.py`, `task_base.py`, `checkin_task.py`, `http.py`, `config.py`, `logger.py`).
- `checkin/xiaojuchongdian/skill/`: skill artifacts grouped by use case (`overall/`, `checkin/`, `get-params/`).
- `docs/requirements/`, `docs/design/`, `docs/standards/`, `docs/analysis/`: product requirements, technical design, coding conventions, and analysis.
- Root-level runtime/context files: `README.md`, `CLAUDE.md`, `.env.example`.

## Build, Test, and Development Commands
- `python3 -m pip install requests`: install runtime dependency.
- `cp .env.example .env`: create local config, then fill `DAILYHUB_XIAOJU_*` values.
- `python3 -m checkin.xiaojuchongdian.src.main list`: list registered tasks.
- `python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin`: query today’s status.
- `python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record`: run idempotent check-in with record verification.
- `python3 -m ruff check checkin` and `python3 -m black checkin docs`: lint/format per standards (install tools if missing).

## Documentation-First Workflow
- For new features or integrations, update docs before code: requirements in `docs/requirements/`, design in `docs/design/`.
- Keep the `_Last updated: YYYY-MM-DD_` footer in changed docs.

## Coding Style & Naming Conventions
- Target Python 3.10+, PEP 8, 4-space indentation.
- Add type hints for public functions/interfaces.
- Naming: classes `PascalCase`, functions/variables `snake_case`, constants `UPPER_SNAKE_CASE`.
- Keep platform logic isolated per module; avoid hardcoded URLs, credentials, and silent `except` blocks.

## Testing Guidelines
- There is no committed automated test suite yet; use CLI smoke checks before submitting changes (`--help`, `list`, `status`, `run`).
- For new logic, add `pytest` tests under `tests/` with `test_*.py` naming, covering router behavior, config validation, and task success/failure branches.

## Commit & Pull Request Guidelines
- The repository currently has no commit history; follow the documented Conventional Commit style from `docs/standards/project-conventions.md`.
- Example commits: `feat(xiaoju): add sign record retry handling`, `docs(standards): clarify env naming`.
- Branch naming: `feat/{platform}-{feature}` or `fix/{issue}`.
- PRs should include purpose, key changes, linked docs updates, verification commands/results, and sanitized output snippets for behavior changes.

## Security & Configuration Tips
- Never commit real `ticket`, `token`, or `token_id` values.
- Use `DAILYHUB_{PLATFORM}_{KEY}` environment variable naming and keep local secrets in `.env` only.
