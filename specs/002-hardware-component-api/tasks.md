# Tasks: Hardware Component API & Project Restructure

**Input**: Design documents from `/specs/002-hardware-component-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included — the spec explicitly requires test suite execution (US3) and the project uses pytest with pytest-django.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Remove the sample app, create the new multi-app project structure, and update configuration

- [x] T001 Remove the `sample/` app directory and its references from `config/settings.py` and `config/urls.py` (FR-008; verified clean in T033)
- [x] T002 Create `components/` app directory structure: `components/__init__.py`, `components/apps.py`, `components/admin.py`, `components/models.py`, `components/serializers.py`, `components/views.py`, `components/urls.py`
- [x] T003 [P] Create `cpu/` app directory structure: `cpu/__init__.py`, `cpu/apps.py`, `cpu/admin.py`, `cpu/models.py`, `cpu/serializers.py`, `cpu/views.py`, `cpu/urls.py`
- [x] T004 [P] Create `dram/` app directory structure: `dram/__init__.py`, `dram/apps.py`, `dram/admin.py`, `dram/models.py`, `dram/serializers.py`, `dram/views.py`, `dram/urls.py`
- [x] T005 Register `components`, `cpu`, and `dram` apps in `config/settings.py` INSTALLED_APPS (replacing `sample`)
- [x] T006 Update `config/urls.py` to include URL patterns for `components`, `cpu`, and `dram` apps (replacing `sample` URLs)
- [x] T007 Update `tests/conftest.py` to remove sample fixtures and prepare for component fixtures
- [x] T007a [P] Verify `pytest.ini` and `setup.cfg` exist and update test paths/coverage settings to reference `components`, `cpu`, `dram` apps (replacing `sample` references)

**Checkpoint**: Project compiles with empty apps registered, sample app fully removed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base Component model and migrations that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Implement `Component` base model in `components/models.py` with fields: `id` (UUID PK), `name` (CharField 255), `component_type` (CharField 50), `description` (TextField optional), `created_at` (DateTimeField auto), `updated_at` (DateTimeField auto); add `Meta.indexes` for `component_type` and `created_at`
- [x] T009 Implement `ComponentSerializer` in `components/serializers.py` with all base fields (id, name, component_type, description, created_at, updated_at); id/created_at/updated_at read-only
- [x] T010 Generate and verify migration for `components` app via `python manage.py makemigrations components`
- [x] T011 Register `Component` model in `components/admin.py`

**Checkpoint**: Foundation ready — `Component` model migrated, base serializer available for child apps

---

## Phase 3: User Story 1 — Query Components Across All Types (Priority: P1) 🎯 MVP

**Goal**: A unified read-only `/api/components/` endpoint that lists and retrieves components across all types with filtering by type, search by name, pagination, and ordering.

**Independent Test**: Create components of different types directly in the DB, then verify the general endpoint returns, filters, paginates, and orders them correctly.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US1] Write tests in `tests/test_components_api.py`: list returns paginated results, filter by `component_type`, search by name, retrieve by UUID, empty list returns 200, ordering by `created_at`/`name`

### Implementation for User Story 1

- [x] T013 [US1] Implement read-only `ComponentViewSet` in `components/views.py` with `list` and `retrieve` actions; configure `PageNumberPagination` (page size 20), `DjangoFilterBackend` filtering on `component_type`, `SearchFilter` on `name`, `OrderingFilter` on `created_at`/`name` (FR-007)
- [x] T014 [US1] Configure router and URL patterns in `components/urls.py` for `/api/components/`
- [x] T015 [US1] Add component fixtures to `tests/conftest.py`: `cpu_component` and `dram_component` factories that create `Component` records with different types

**Checkpoint**: US1 complete — general endpoint serves cross-type read queries with filtering, search, pagination, ordering

---

## Phase 4: User Story 2 — Manage Components via Type-Specific Endpoints (Priority: P2)

**Goal**: Dedicated `/api/cpu/` and `/api/dram/` endpoints with full CRUD, type-specific fields, and validation. Components created here automatically appear in the general endpoint (US1).

**Independent Test**: CRUD operations on each type-specific endpoint; verify data appears in general endpoint; verify validation rejects invalid data.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US2] Write CPU CRUD tests in `tests/test_cpu_api.py`: create with valid data (201), list (200), retrieve by UUID (200), full update via PUT (200), partial update via PATCH (200), delete (204), validation errors for missing required fields (400), validation that `threads >= cores` and `boost_clock >= clock_speed`
- [x] T017 [P] [US2] Write DRAM CRUD tests in `tests/test_dram_api.py`: create with valid data (201), list (200), retrieve by UUID (200), full update via PUT (200), partial update via PATCH (200), delete (204), validation errors for missing required fields (400)
- [x] T018 [P] [US2] Write cross-endpoint tests in `tests/test_components_api.py` (append): creating a CPU/DRAM via type endpoint makes it appear in `/api/components/`, deleting via type endpoint removes it from general endpoint

### Implementation for User Story 2

- [x] T019 [US2] Implement `CpuComponent` model in `cpu/models.py` inheriting from `Component` with fields: `cores` (PositiveIntegerField), `threads` (PositiveIntegerField), `clock_speed` (DecimalField 5,2), `boost_clock` (DecimalField 5,2 optional), `tdp` (PositiveIntegerField optional), `socket` (CharField 50 optional); override `save()` to auto-set `component_type = "cpu"`
- [x] T020 [P] [US2] Implement `DramComponent` model in `dram/models.py` inheriting from `Component` with fields: `capacity_gb` (PositiveIntegerField), `speed_mhz` (PositiveIntegerField), `ddr_type` (CharField 10), `modules` (PositiveIntegerField optional default 1), `cas_latency` (PositiveIntegerField optional), `voltage` (DecimalField 3,2 optional); override `save()` to auto-set `component_type = "dram"`
- [x] T021 Generate and verify migrations for `cpu` and `dram` apps via `python manage.py makemigrations cpu dram`
- [x] T022 [US2] Implement `CpuComponentSerializer` in `cpu/serializers.py` with all CPU fields plus inherited base fields; add validation: `threads >= cores`, `boost_clock >= clock_speed` (if provided), `cores >= 1`, `clock_speed > 0`; `component_type` read-only (auto-set)
- [x] T023 [P] [US2] Implement `DramComponentSerializer` in `dram/serializers.py` with all DRAM fields plus inherited base fields; add validation: `capacity_gb > 0`, `speed_mhz > 0`; `component_type` read-only (auto-set)
- [x] T024 [US2] Implement `CpuComponentViewSet` in `cpu/views.py` as `ModelViewSet` with full CRUD; add `SearchFilter` on `name`, `OrderingFilter` on `created_at`/`name`/`cores`/`clock_speed`
- [x] T025 [P] [US2] Implement `DramComponentViewSet` in `dram/views.py` as `ModelViewSet` with full CRUD; add `SearchFilter` on `name`, `OrderingFilter` on `created_at`/`name`/`capacity_gb`/`speed_mhz`
- [x] T026 [P] [US2] Configure router and URL patterns in `cpu/urls.py` for `/api/cpu/`
- [x] T027 [P] [US2] Configure router and URL patterns in `dram/urls.py` for `/api/dram/`
- [x] T028 [P] [US2] Register `CpuComponent` in `cpu/admin.py` and `DramComponent` in `dram/admin.py`
- [x] T029 [US2] Add CPU and DRAM component fixtures to `tests/conftest.py`: factories that create full `CpuComponent` and `DramComponent` instances with type-specific fields

**Checkpoint**: US2 complete — type-specific CRUD works, cross-endpoint visibility confirmed, validation enforced

---

## Phase 5: User Story 3 — Run Tests in Container Environment (Priority: P3)

**Goal**: A single `docker compose` command runs the full test suite inside the container environment against PostgreSQL.

**Independent Test**: Run `docker compose run --rm web pytest` and verify all tests pass with clear output.

### Implementation for User Story 3

- [x] T030 [US3] Update `docker-compose.yml` to add a `test` profile or verify existing setup supports `docker compose run --rm web pytest`
- [x] T031 [US3] Update `entrypoint.sh` to detect pytest execution and run migrations before tests (if not already handled)
- [x] T032 [US3] Run full test suite in container mode via `docker compose run --rm web pytest -v` and verify all tests pass; also verify that if the container DB is unavailable the suite fails fast with a clear connection error (not a hang)

**Checkpoint**: US3 complete — container test execution works with clear pass/fail output

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, documentation, and validation across all stories

- [x] T033 Remove old `sample/` migration files and verify no stale `sample` references remain in codebase (completes FR-008 cleanup started in T001)
- [x] T034 [P] Update `.env.example` if any new environment variables were added
- [x] T035 [P] Run `ruff check .` and fix any linting issues across all new files
- [x] T036 Validate quickstart.md scenarios: start containers, hit all endpoints (components, cpu, dram), create/read/update/delete via curl
- [x] T037 Run full test suite locally (`pytest -v`) and verify 100% pass rate
- [x] T038 Validate FR-009 repeatable-type pattern: confirm that adding a new component type requires only creating a new app + registering URLs — no changes to `components/` app code or general endpoint logic

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — base model and serializer must exist
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — child models inherit from Component. Also depends on US1 for cross-endpoint tests (T018)
- **US3 (Phase 5)**: Depends on US1 + US2 — needs working tests to run in container
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. No dependencies on other stories.
- **US2 (P2)**: Can start after Phase 2. Cross-endpoint tests (T018) verify integration with US1 but US2 implementation is independent.
- **US3 (P3)**: Depends on US1 + US2 having passing tests to validate container execution.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before serializers
- Serializers before views
- Views before URL configuration
- Core implementation before integration/cross-endpoint tests

### Parallel Opportunities

**Phase 1**: T003 and T004 can run in parallel (independent app directories); T007a parallel with T007
**Phase 3**: T012 (test writing) is independent
**Phase 4**: T016, T017, T018 (test writing) can all run in parallel; T020 parallel with T019; T023 parallel with T022; T025, T026, T27, T028 can all run in parallel
**Phase 6**: T034 and T035 can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Write CPU CRUD tests in tests/test_cpu_api.py"         # T016
Task: "Write DRAM CRUD tests in tests/test_dram_api.py"       # T017
Task: "Write cross-endpoint tests in tests/test_components_api.py"  # T018

# Launch CPU and DRAM models in parallel:
Task: "Implement CpuComponent model in cpu/models.py"         # T019
Task: "Implement DramComponent model in dram/models.py"       # T020

# Launch CPU and DRAM serializers in parallel:
Task: "Implement CpuComponentSerializer in cpu/serializers.py" # T022
Task: "Implement DramComponentSerializer in dram/serializers.py" # T023

# Launch independent view/url/admin tasks in parallel:
Task: "Implement DramComponentViewSet in dram/views.py"        # T025
Task: "Configure router in cpu/urls.py"                        # T026
Task: "Configure router in dram/urls.py"                       # T027
Task: "Register models in admin"                               # T028
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (remove sample, create app shells)
2. Complete Phase 2: Foundational (Component base model + serializer)
3. Complete Phase 3: User Story 1 (general read-only endpoint)
4. **STOP and VALIDATE**: Test US1 independently — list, filter, search, paginate
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (full CRUD per type)
4. Add User Story 3 → Validate container tests → Deploy/Demo (CI-ready)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (general endpoint)
   - Developer B: User Story 2 (type-specific CRUD)
3. US3 follows once US1+US2 have passing tests

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD: Red → Green → Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
