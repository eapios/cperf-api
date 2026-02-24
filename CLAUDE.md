# cperf-api Development Guidelines

Last Updated: 2026-02-24

## Stack
- Python 3.12 + Django 5.1 + DRF 3.15
- django-environ, django-filter, psycopg2-binary
- PostgreSQL 16 (Docker), SQLite 3 (local, default when `DATABASE_URL` unset)

## Project Structure

```text
config/        # Django project package (settings, urls)
cpu/           # CPU component app
dram/          # DRAM component app
nand/          # NAND component app
properties/    # Extended properties app
results/       # Test results app
tests/         # pytest test suite
docs/          # API, architecture, and TypeScript model docs
requirements/  # base.txt + dev.txt
```

## Commands

```bash
pytest        # run tests (config via pytest.ini)
ruff check .  # lint
black .       # format
```

## Environment
- Copy `.env.example` → `.env` for local dev
- Env file priority: `.env.local` > `.env` (shell/Docker vars always win — `overrides=False`)
- `DATABASE_URL` defaults to SQLite when unset
- Docker requires: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SECRET_KEY`
- Auto-superuser on container start if `DJANGO_SUPERUSER_USERNAME` + `DJANGO_SUPERUSER_PASSWORD` set

## Docker
```bash
docker-compose up       # start with PostgreSQL
docker-compose up web   # web only (requires db already running)
```

## Gotchas
- Container entrypoint auto-runs `migrate` + `ensure_superuser` on every start
- DRF defaults: `AllowAny` (no auth), page size 20, filter/ordering/search enabled globally
- `DJANGO_SETTINGS_MODULE=config.settings` (set in `pytest.ini` — not needed manually for tests)

<!-- MANUAL ADDITIONS START -->

## Documentation Sync Rules

When making code changes, **always** update the corresponding documentation:

| What Changed | Update |
|---|---|
| Models (fields, validation, new component type) | `docs/architecture.md` data model section, `docs/api.md` request/response examples, `docs/models.ts` TypeScript interfaces |
| URLs / Views / Serializers (endpoints, methods, query params) | `docs/api.md` affected endpoint section |
| Dockerfile, docker-compose.yml, entrypoint.sh | `README.md` Docker setup section |
| requirements/*.txt | `README.md` prerequisites section |
| settings.py (env vars, installed apps) | `README.md` environment section, `docs/architecture.md` tech stack |
| Any feature added/changed/fixed/removed | `CHANGELOG.md` under `[Unreleased]` section |

After updating any doc, bump the `Last Updated: YYYY-MM-DD` line in that file.

<!-- MANUAL ADDITIONS END -->
