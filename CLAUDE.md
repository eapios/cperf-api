# cperf-api Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-06

## Active Technologies
- PostgreSQL 16 (container), SQLite 3 (local debug) (002-hardware-component-api)
- N/A (documentation-only feature) (003-project-docs)
- Python 3.12 + Django 5.1, Django REST Framework 3.15, django-environ, psycopg2-binary, debugpy (001-drf-docker-setup)
- Python 3.12 + Django 5.1 + Django (built-in auth framework, management commands) (004-auto-superuser)
- PostgreSQL 16 (Docker), SQLite 3 (local) — uses existing `django.contrib.auth` User model (004-auto-superuser)
- Python 3.12 + Django 5.1 + Django REST Framework 3.15, django-environ, django-filter, psycopg2-binary (005-model-redesign)
- PostgreSQL 16 (Docker), SQLite 3 (local debug) (005-model-redesign)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.12: Follow standard conventions

## Recent Changes
- 005-model-redesign: Added Python 3.12 + Django 5.1 + Django REST Framework 3.15, django-environ, django-filter, psycopg2-binary
- 004-auto-superuser: Added Python 3.12 + Django 5.1 + Django (built-in auth framework, management commands)
- 003-project-docs: Added N/A (documentation-only feature)

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
