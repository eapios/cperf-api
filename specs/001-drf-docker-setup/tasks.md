# Tasks: RESTful API Backend Initialization

**Input**: Design documents from `/specs/001-drf-docker-setup/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Not explicitly requested in spec. Basic test infrastructure included in Polish phase.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Exact file paths included in descriptions

## Path Conventions

Based on plan.md structure: Django project with `config/` package and `sample/` app at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency files, and tooling configuration

- [x] T001 Create project directory structure: `config/`, `sample/`, `sample/migrations/`, `tests/`, `requirements/`, `.vscode/`
- [x] T002 Create `requirements/base.txt` with Django 5.1, djangorestframework 3.15, django-environ, psycopg2-binary
- [x] T003 Create `requirements/dev.txt` with `-r base.txt`, pytest, pytest-django, debugpy
- [x] T004 [P] Create `.gitignore` with Python, Django, Docker, VS Code, .env, .env.local, db.sqlite3, __pycache__ patterns
- [x] T005 [P] Create `.env.example` with template variables: SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, APP_PORT (default 8000)
- [x] T006 [P] Create `.dockerignore` with .venv, .git, __pycache__, *.pyc, .env.local, db.sqlite3, specs/, .vscode/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Django project configuration that MUST be complete before ANY user story can be implemented

**Warning**: No user story work can begin until this phase is complete

- [x] T007 Create `config/__init__.py` (empty)
- [x] T008 Create `config/settings.py` using django-environ: SECRET_KEY with default, DEBUG=True default, ALLOWED_HOSTS, DATABASES via DATABASE_URL defaulting to `sqlite:///db.sqlite3`, INSTALLED_APPS with rest_framework and sample app, REST_FRAMEWORK config with default pagination and ordering, STATIC_URL, DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
- [x] T009 Create `manage.py` with DJANGO_SETTINGS_MODULE defaulting to `config.settings`
- [x] T010 [P] Create `config/urls.py` with admin URL and API URL include placeholder for `sample.urls`
- [x] T011 [P] Create `config/wsgi.py` with DJANGO_SETTINGS_MODULE pointing to `config.settings`
- [x] T012 [P] Create `config/asgi.py` with DJANGO_SETTINGS_MODULE pointing to `config.settings`
- [x] T013 [P] Create `setup.cfg` with black (line-length=88), isort (profile=black), and flake8 configuration
- [x] T014 [P] Create `pytest.ini` with DJANGO_SETTINGS_MODULE=config.settings and pythonpath=.

**Checkpoint**: Django project boots with `python manage.py check` — user story implementation can begin

---

## Phase 3: User Story 1 - One-Command Environment Setup (Priority: P1) MVP

**Goal**: Start the entire backend environment (app server + database) with a single `docker compose up` command

**Independent Test**: Run `docker compose up --build` on a clean clone and verify both containers start, the server responds at http://localhost:8000/, and data persists across restarts

### Implementation for User Story 1

- [x] T015 [US1] Create `Dockerfile` using `python:3.12-slim` base, install system deps (libpq-dev, gcc), copy and install requirements/base.txt, copy app code, set PYTHONUNBUFFERED=1 and PYTHONDONTWRITEBYTECODE=1, EXPOSE 8000, set entrypoint to `entrypoint.sh`
- [x] T016 [US1] Create `entrypoint.sh` with: pg_isready wait loop (max 30 retries, 2s interval), `python manage.py migrate --noinput`, then `exec "$@"` to pass through CMD
- [x] T017 [US1] Create `docker-compose.yml` with two services: `db` (postgres:16, named volume `postgres_data`, healthcheck via pg_isready, env vars from .env) and `web` (build from Dockerfile, depends_on db with condition service_healthy, ports `${APP_PORT:-8000}:8000` for configurable host port per FR-003, volume mount `.:/app` for live code sync, env vars DATABASE_URL/SECRET_KEY/DEBUG/ALLOWED_HOSTS, command `python manage.py runserver 0.0.0.0:8000`)
- [x] T018 [US1] Create `.env` with Docker-specific values: DATABASE_URL=postgres://cperf:cperf@db:5432/cperf, SECRET_KEY=dev-secret-change-in-production, DEBUG=True, ALLOWED_HOSTS=localhost,127.0.0.1, POSTGRES_DB=cperf, POSTGRES_USER=cperf, POSTGRES_PASSWORD=cperf, APP_PORT=8000

**Checkpoint**: `docker compose up --build` starts both containers, server responds at localhost:8000, `docker compose down && docker compose up` preserves data

---

## Phase 4: User Story 2 - RESTful API Endpoint Access (Priority: P2)

**Goal**: Working CRUD API for SampleItem with browsable interface at `/api/items/`

**Independent Test**: Send GET/POST/PUT/PATCH/DELETE requests to http://localhost:8000/api/items/ and verify correct responses per OpenAPI contract in `contracts/openapi.yaml`

### Implementation for User Story 2

- [x] T019 [P] [US2] Create `sample/__init__.py` (empty) and `sample/apps.py` with SampleConfig (name='sample')
- [x] T020 [US2] Create `sample/models.py` with SampleItem model: id (UUIDField, primary_key, default=uuid4, editable=False), name (CharField, max_length=255), description (TextField, blank=True, null=True), created_at (DateTimeField, auto_now_add=True, db_index=True), updated_at (DateTimeField, auto_now=True). Add Meta class with ordering=['-created_at']
- [x] T021 [US2] Generate initial migration by running `python manage.py makemigrations sample` to create `sample/migrations/0001_initial.py`
- [x] T022 [US2] Create `sample/serializers.py` with SampleItemSerializer (ModelSerializer): fields=[id, name, description, created_at, updated_at], read_only_fields=[id, created_at, updated_at], validate name is non-blank
- [x] T023 [US2] Create `sample/views.py` with SampleItemViewSet (ModelViewSet): queryset=SampleItem.objects.all(), serializer_class=SampleItemSerializer, ordering_fields=[name, created_at], search_fields=[name]
- [x] T024 [US2] Create `sample/urls.py` with DefaultRouter registering SampleItemViewSet at 'items'
- [x] T025 [US2] Update `config/urls.py` to include `sample.urls` under `api/` prefix and ensure rest_framework browsable API URLs are included

**Checkpoint**: Full CRUD works: POST creates items (201), GET lists/retrieves (200), PUT/PATCH updates (200), DELETE removes (204), invalid data returns 400, missing items return 404, browser shows browsable API

---

## Phase 5: User Story 5 - Local F5 Debug Mode (Priority: P2)

**Goal**: Press F5 in VS Code to start Django in debug mode with breakpoints, using SQLite by default and optionally Docker PostgreSQL

**Independent Test**: Open project in VS Code, press F5, verify server starts at localhost:8000, set breakpoint in sample/views.py, send request, confirm breakpoint is hit

### Implementation for User Story 5

- [x] T026 [P] [US5] Create `.vscode/launch.json` with configuration: name="Django: F5 Debug", type=debugpy, request=launch, program="${workspaceFolder}/manage.py", args=["runserver", "--noreload", "127.0.0.1:8000"], django=true, justMyCode=false, envFile="${workspaceFolder}/.env.local", env={DJANGO_SETTINGS_MODULE: config.settings}
- [x] T027 [P] [US5] Create `.vscode/settings.json` with: python.defaultInterpreterPath="${workspaceFolder}/.venv/bin/python", python.testing.pytestEnabled=true, python.testing.pytestArgs=["tests"], editor.formatOnSave=true, python.formatting.provider=black, files.exclude for __pycache__ and .pytest_cache
- [x] T028 [US5] Create `.env.local` with comment explaining it defaults to SQLite (no DATABASE_URL set) and a commented-out DATABASE_URL=postgres://cperf:cperf@localhost:5432/cperf line for switching to Docker PostgreSQL

**Checkpoint**: F5 starts Django in debug mode with SQLite, breakpoints work, uncommenting DATABASE_URL in .env.local switches to Docker PostgreSQL (after running `docker compose up db -d`)

---

## Phase 6: User Story 3 - Database Administration Access (Priority: P3)

**Goal**: Django admin interface at `/admin/` showing SampleItem model with full CRUD

**Independent Test**: Navigate to http://localhost:8000/admin/, log in with superuser credentials, verify SampleItem list/detail/create/edit/delete all work

### Implementation for User Story 3

- [x] T029 [US3] Create `sample/admin.py` with SampleItemAdmin: list_display=[name, created_at, updated_at], list_filter=[created_at], search_fields=[name, description], readonly_fields=[id, created_at, updated_at], ordering=['-created_at']
- [x] T030 [US3] Document superuser creation command in a comment at top of `entrypoint.sh`: `docker compose exec web python manage.py createsuperuser` (or `python manage.py createsuperuser` for local mode)

**Checkpoint**: Admin interface accessible, SampleItem visible and editable, records created via API appear in admin

---

## Phase 7: User Story 4 - Development Workflow with Live Reload (Priority: P4)

**Goal**: Code changes on host machine reflected in running Docker containers within 5 seconds without restart

**Independent Test**: With containers running, edit a string in sample/views.py, verify the change appears in API response without restarting containers

### Implementation for User Story 4

- [x] T031 [US4] Verify `docker-compose.yml` volume mount (`.:/app`) correctly syncs host code into the web container, and that `python manage.py runserver` auto-reload is active (runserver is already configured in T017 CMD). If needed, ensure no `.dockerignore` conflicts prevent code sync

**Checkpoint**: Edit sample/views.py while containers run, save file, send API request within 5 seconds, see updated behavior. Syntax errors show in `docker compose logs web` without crashing container.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Test infrastructure, documentation validation, and final quality checks

- [x] T032 [P] Create `tests/__init__.py` (empty) and `tests/conftest.py` with shared pytest fixtures: api_client (DRF APIClient), sample_item (factory creating a SampleItem instance)
- [x] T033 [P] Create `tests/test_sample_api.py` with CRUD smoke tests: test_list_empty, test_create_item, test_retrieve_item, test_update_item, test_partial_update_item, test_delete_item, test_create_invalid_returns_400, test_retrieve_nonexistent_returns_404
- [x] T034 Validate quickstart.md by running through Docker mode workflow (clone, docker compose up, verify endpoints)
- [x] T035 Validate quickstart.md by running through local F5 debug mode workflow (venv setup, F5, verify endpoints)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) - Docker infrastructure
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) - Can start in parallel with US1
- **US5 (Phase 5)**: Depends on Foundational (Phase 2) - Can start in parallel with US1 and US2
- **US3 (Phase 6)**: Depends on US2 (needs SampleItem model and admin registration)
- **US4 (Phase 7)**: Depends on US1 (needs Docker Compose running) and US2 (needs code to verify reload)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends only on Phase 2 - no story-to-story dependencies
- **US2 (P2)**: Depends only on Phase 2 - no story-to-story dependencies
- **US5 (P2)**: Depends only on Phase 2 - no story-to-story dependencies
- **US3 (P3)**: Depends on US2 (needs SampleItem model defined in sample/models.py)
- **US4 (P4)**: Depends on US1 (needs docker-compose.yml) and US2 (needs app code to reload)

### Within Each User Story

- Models before serializers
- Serializers before views
- Views before URL configuration
- URL configuration before integration with config/urls.py

### Parallel Opportunities

- T004 + T005 + T006 can run in parallel (Phase 1: .gitignore, .env.example, .dockerignore)
- T010 + T011 + T012 + T013 + T014 can all run in parallel (Phase 2: independent config files)
- US1, US2, and US5 can all start in parallel after Phase 2 completes
- T026 + T027 can run in parallel (Phase 5: launch.json and settings.json)
- T032 + T033 can run in parallel (Phase 8: test files)

---

## Parallel Example: After Phase 2 Completes

```text
# Three stories can launch simultaneously:

# Stream 1: US1 - Docker Setup
Task: T015 [US1] Create Dockerfile
Task: T016 [US1] Create entrypoint.sh
Task: T017 [US1] Create docker-compose.yml
Task: T018 [US1] Create .env

# Stream 2: US2 - API Endpoints
Task: T019 [US2] Create sample app boilerplate
Task: T020 [US2] Create SampleItem model
Task: T021 [US2] Generate migration
...

# Stream 3: US5 - VS Code Debug
Task: T026 [US5] Create launch.json
Task: T027 [US5] Create settings.json
Task: T028 [US5] Create .env.local
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T014)
3. Complete Phase 3: US1 - Docker Environment (T015-T018)
4. **STOP and VALIDATE**: `docker compose up --build` works, server responds, data persists
5. This is a deployable MVP - containerized Django running with PostgreSQL

### Incremental Delivery

1. Setup + Foundational → Django project boots locally
2. Add US1 (Docker) → Full containerized environment (MVP!)
3. Add US2 (API) → CRUD endpoints working with browsable interface
4. Add US5 (Debug) → VS Code F5 debugging with switchable DB
5. Add US3 (Admin) → Django admin for data inspection
6. Add US4 (Reload) → Verify live reload in Docker
7. Polish → Tests, documentation validation, cleanup

### Recommended Execution Order (Single Developer)

Phase 1 → Phase 2 → US2 → US1 → US5 → US3 → US4 → Polish

Rationale: Building the Django app code (US2) first lets you verify it locally before containerizing (US1). Then add VS Code debug (US5), admin (US3), and verify reload (US4).

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- No test-first workflow requested; basic tests in Polish phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total: 35 tasks across 8 phases
