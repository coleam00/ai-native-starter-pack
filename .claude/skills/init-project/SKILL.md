---
name: init-project
description: Set up and run THIS project locally from a fresh clone — environment, dependencies, database/services, migrations, seed, and the dev server. Reads the project's own setup docs rather than assuming.
---

# Initialize project locally

Read the project's `README`, `.env.example`, `docker-compose.yml`, and
`pyproject.toml` / `package.json` first, then use the real values for this project.

## Typical steps

1. **Env:** `cp .env.example .env` and fill in required values.
2. **Dependencies:** install them (`uv sync` / `npm install` / `poetry install` / …).
3. **Services:** start the DB/queue (`docker compose up -d` if there's a compose file).
4. **Migrations:** apply them (`alembic upgrade head` / `prisma migrate dev` / …).
5. **Seed:** run any seed/fixtures command the project provides.
6. **Run:** start the dev server(s).

## Validate

Hit the health endpoint or open the app and confirm it loads.

## Notes

- Exact ports, service names, and commands differ per project — always check the repo's
  own config and README rather than assuming defaults.
