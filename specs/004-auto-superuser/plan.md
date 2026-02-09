# Implementation Plan: Auto-Create Superuser

**Branch**: `004-auto-superuser` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-auto-superuser/spec.md`

## Summary

Automatically create a Django superuser on application startup using environment variables, so developers can immediately access `/admin` without running `createsuperuser` manually. Implemented as a custom Django management command called from the existing `entrypoint.sh`.

## Technical Context

**Language/Version**: Python 3.12 + Django 5.1
**Primary Dependencies**: Django (built-in auth framework, management commands)
**Storage**: PostgreSQL 16 (Docker), SQLite 3 (local) — uses existing `django.contrib.auth` User model
**Testing**: pytest + pytest-django
**Target Platform**: Linux container (Docker), Windows/macOS (local dev)
**Project Type**: Web application (Django REST API)
**Performance Goals**: N/A — runs once at startup
**Constraints**: Must not fail or block application startup
**Scale/Scope**: Single management command + entrypoint change + env vars

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is not yet configured (blank template). No gates to enforce. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/004-auto-superuser/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
config/
├── management/
│   └── commands/
│       └── ensure_superuser.py   # Custom management command
├── settings.py                    # No changes needed
├── urls.py                        # No changes needed
└── wsgi.py

entrypoint.sh                      # Add ensure_superuser call after migrate
docker-compose.yml                 # Add DJANGO_SUPERUSER_* env vars
.env.example                       # Add DJANGO_SUPERUSER_* examples
tests/
└── test_ensure_superuser.py       # Unit tests for the command
```

**Structure Decision**: The management command lives in `config/management/commands/` since it's a project-level concern (not app-specific). This follows Django convention for commands that span the whole project.

## Complexity Tracking

No constitution violations — feature is minimal scope.
