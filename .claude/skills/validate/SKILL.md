---
name: validate
description: Run THIS project's full quality gate — tests, type-check, lint, and (for full-stack) the build — and report overall health with ✅/❌. Use before opening a PR; this is the gate that runs BEFORE the PR, not after.
---

# Validate

Run the project's validation suite and report results clearly. **Use the real commands for
this project** — check `pyproject.toml` / `package.json` / `Makefile` / `README`, and the
CI workflow, for the actual ones. Mirror what CI runs so "green locally" means "green in CI."

## Typical backend (Python)

```bash
uv run pytest -q          # tests   (or: pytest / poetry run pytest)
uv run mypy <package>     # type check
uv run ruff check <package>   # lint
```

## Typical frontend (TS/JS)

```bash
npm run build             # production build
npx tsc --noEmit          # type check   (or: npm run lint / npm test)
```

## Optional live smoke

Start the app per the project's run command and hit its health endpoint.

## Summary report

- Tests passed/failed
- Type check
- Lint
- Build (if applicable)
- Overall health: **PASS / FAIL**

## Notes

- Any code path that emits a datetime / locale-sensitive / tenant-scoped value should have
  a test for a non-default case — that's the kind of regression guard that catches the
  bugs reviews miss.
