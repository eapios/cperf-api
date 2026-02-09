# Implementation Plan: RESTful API Backend Initialization

**Branch**: `001-drf-docker-setup` | **Date**: 2026-02-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-drf-docker-setup/spec.md`

## Summary

Initialize a containerized Django REST Framework API backend with PostgreSQL, including a sample CRUD resource, Django admin, browsable API, and VS Code F5 debug mode with switchable SQLite/PostgreSQL database. The project uses Docker Compose for full-stack orchestration and supports local development with debugpy integration.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Django 5.1, Django REST Framework 3.15, django-environ, psycopg2-binary, debugpy
**Storage**: PostgreSQL 16 (Docker mode), SQLite 3 (local debug default), switchable via `DATABASE_URL`
**Testing**: pytest with pytest-django
**Target Platform**: Linux containers (Docker), local Windows/macOS/Linux for debug
**Project Type**: Web (API backend only, no frontend)
**Performance Goals**: CRUD operations < 1 second, container startup < 2 minutes
**Constraints**: Environment startup < 2 min, code reload < 10 sec, F5 debug start < 30 sec
**Scale/Scope**: Development environment for single-team use; production deployment out of scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is unpopulated (template placeholders only). No active gates to evaluate. Proceeding without violations.

**Post-Phase 1 re-check**: No violations. Project structure follows standard Django conventions with minimal complexity.

## Project Structure

### Documentation (this feature)

```text
specs/001-drf-docker-setup/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer quickstart guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml     # OpenAPI 3.1 specification
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
cperf-api/
├── config/                      # Django project configuration package
│   ├── __init__.py
│   ├── settings.py              # Environment-driven settings (single file)
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application entry point
│   └── asgi.py                  # ASGI application entry point
├── sample/                      # Sample app (reference CRUD implementation)
│   ├── __init__.py
│   ├── admin.py                 # Admin site registration
│   ├── apps.py                  # App configuration
│   ├── models.py                # SampleItem model
│   ├── serializers.py           # DRF serializers
│   ├── views.py                 # ModelViewSet
│   ├── urls.py                  # Router-based URL configuration
│   └── migrations/              # Database migrations
│       └── 0001_initial.py
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_sample_api.py       # CRUD endpoint tests
├── manage.py                    # Django management script
├── Dockerfile                   # Application container image
├── docker-compose.yml           # Docker Compose orchestration
├── entrypoint.sh                # Container entrypoint (DB wait + migrate)
├── requirements/                # Dependency management
│   ├── base.txt                 # Production dependencies
│   └── dev.txt                  # Development dependencies (includes base)
├── .env.example                 # Environment variable template (committed)
├── .env                         # Docker environment variables (gitignored)
├── .env.local                   # Local debug environment overrides (gitignored)
├── .vscode/                     # VS Code workspace configuration
│   ├── launch.json              # F5 debug launch configuration
│   └── settings.json            # Python/Django workspace settings
├── .gitignore                   # Git ignore rules
├── pytest.ini                   # Pytest configuration
└── setup.cfg                    # Tool configuration (black, isort, flake8)
```

**Structure Decision**: Standard Django project layout with `config/` as the project package (instead of the default project-named directory). This is a single-project, backend-only structure. Each domain feature gets its own Django app directory at the repository root. The `sample/` app serves as the reference implementation pattern.

## Key Design Decisions

### D-001: Single Settings File with Environment Variables

Rather than split settings (base/local/production), a single `config/settings.py` uses `django-environ` to read all configuration from environment variables with sensible defaults. This means:

- **No `.env` file needed for local debug**: Defaults point to SQLite, DEBUG=True, localhost
- **Docker mode**: `.env` file provides PostgreSQL connection, secret key
- **Switching databases**: Change `DATABASE_URL` in `.env.local` (one variable, per SC-008)

### D-002: Entrypoint Script for Container Readiness

The `entrypoint.sh` script:
1. Waits for PostgreSQL to accept connections (loop with `pg_isready`)
2. Runs `python manage.py migrate --noinput`
3. Executes the passed CMD (runserver)

This satisfies FR-009 (auto-migrate) and FR-011 (DB retry).

### D-003: VS Code Debug with debugpy

The `.vscode/launch.json` configures:
- Program: `manage.py`
- Args: `runserver --noreload` (debugpy handles the process; Django's built-in reloader conflicts with debugpy)
- envFile: `.env.local` (defaults to SQLite when file doesn't exist)
- justMyCode: false (allows stepping into DRF/Django internals if needed)

### D-004: UUID Primary Keys

Using UUIDs instead of auto-incrementing integers for the SampleItem model. This prevents information disclosure (sequential IDs reveal record count) and makes the API more portable across database backends (SQLite and PostgreSQL both support UUIDs).

## Complexity Tracking

No constitution violations to justify. The project uses standard Django patterns with minimal abstraction.
