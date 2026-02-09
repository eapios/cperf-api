# Tasks: Project Documentation Suite

**Input**: Design documents from `/specs/003-project-docs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Tests**: Not applicable — documentation-only feature. Verification is manual (see quickstart.md).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All files at repository root or under `docs/`
- Agent rules under `.claude/rules/`

---

## Phase 1: Setup

**Purpose**: Create directories and foundational files

- [x] T001 Create `docs/` directory at repository root
- [x] T002 [P] Create MIT License file at `LICENSE` with copyright 2026 cperf-api contributors (FR-009)

**Checkpoint**: Directory structure ready, LICENSE complete

---

## Phase 2: Foundational (Doc Sync Rules — FR-010)

**Purpose**: Ensure future code changes trigger doc updates. Already completed during `/speckit.clarify` session.

- [x] T003 ~~Create doc sync rules at `.claude/rules/doc-sync.md` mapping code change types to affected docs (FR-010)~~
- [x] T004 ~~Add Documentation Sync Rules table to `CLAUDE.md` under MANUAL ADDITIONS markers (FR-010)~~

**Checkpoint**: Agent rules in place — Claude Code will auto-update docs on future code changes

---

## Phase 3: User Story 1 — Developer Onboarding via README (Priority: P1) 🎯 MVP

**Goal**: New developer can set up, run, test, and debug the project by following README alone.

**Independent Test**: Follow the README from a fresh clone. Server starts, tests pass, debugger attaches.

### Implementation for User Story 1

- [x] T005 [US1] Create `README.md` at repository root with project overview section — what cperf-api is, what it does (FR-001)
- [x] T006 [US1] Add Prerequisites section to `README.md` listing Python 3.12, pip, Git, Docker/Docker Compose (optional) with install links (FR-001)
- [x] T007 [US1] Add Quick Start (Local) section to `README.md` — venv creation, `pip install -r requirements/dev.txt`, `python manage.py migrate`, `python manage.py runserver`, verify at localhost:8000 (FR-001, FR-006)
- [x] T008 [US1] Add Quick Start (Docker) section to `README.md` — copy `.env.example` to `.env`, `docker compose up`, verify at localhost:8000, explain PostgreSQL auto-migration via entrypoint.sh (FR-001, FR-006)
- [x] T009 [US1] Add Running Tests section to `README.md` — `pytest` command, mention pytest.ini config, expected 42 passing tests (FR-001)
- [x] T010 [US1] Add Debugging section to `README.md` — debugpy setup for local mode (run with `python -m debugpy --listen 5678 manage.py runserver`), VS Code launch.json attach config, PyCharm remote debug config (FR-005)
- [x] T011 [US1] Add Docker debugging subsection to `README.md` — expose port 5678 in docker-compose override, VS Code attach-to-container config (FR-005)
- [x] T012 [US1] Add Project Structure section to `README.md` — directory tree with brief descriptions of config/, components/, cpu/, dram/, tests/, requirements/, docs/ (FR-001)
- [x] T013 [US1] Add API Overview section to `README.md` — brief endpoint summary table linking to `docs/api.md` for full reference (FR-001)
- [x] T014 [US1] Add License and Last Updated sections to `README.md` — "MIT License" with link to LICENSE file, "Last Updated: 2026-02-09" (FR-008)

**Checkpoint**: README complete — developer can onboard using only this file

---

## Phase 4: User Story 2 — API Consumer Discovers Endpoints (Priority: P2)

**Goal**: Frontend developer or API consumer finds complete endpoint documentation with examples.

**Independent Test**: Every curl example in the doc returns the documented response shape and status code.

### Implementation for User Story 2

- [x] T015 [US2] Create `docs/api.md` with title, base URL (`http://localhost:8000/api/`), and Last Updated date (FR-002, FR-008)
- [x] T016 [US2] Document Components endpoints in `docs/api.md` — `GET /api/components/` (list with pagination, filtering by `component_type`, search by `name`, ordering), `GET /api/components/{id}/` (retrieve by UUID), note read-only (FR-002, FR-007)
- [x] T017 [US2] Document CPU endpoints in `docs/api.md` — `GET /api/cpu/` (list), `POST /api/cpu/` (create with required fields: name, cores, threads, clock_speed), `GET /api/cpu/{id}/`, `PUT /api/cpu/{id}/`, `PATCH /api/cpu/{id}/`, `DELETE /api/cpu/{id}/` with curl examples and example JSON responses (FR-002, FR-007)
- [x] T018 [US2] Document DRAM endpoints in `docs/api.md` — `GET /api/dram/` (list), `POST /api/dram/` (create with required fields: name, capacity_gb, speed_mhz, ddr_type), `GET /api/dram/{id}/`, `PUT /api/dram/{id}/`, `PATCH /api/dram/{id}/`, `DELETE /api/dram/{id}/` with curl examples and example JSON responses (FR-002, FR-007)
- [x] T019 [US2] Add validation rules section to `docs/api.md` — CPU: threads >= cores, boost_clock >= clock_speed; DRAM: name non-blank; common error response shape (FR-002)
- [x] T020 [US2] Add query parameters reference to `docs/api.md` — search, ordering, component_type filter, pagination (page, page_size=20) (FR-002)

**Checkpoint**: API reference complete — every endpoint documented with working curl examples

---

## Phase 5: User Story 3 — Team Tracks Changes via Changelog (Priority: P3)

**Goal**: Team member finds chronological record of all project changes.

**Independent Test**: Each changelog entry corresponds to actual features in the codebase.

### Implementation for User Story 3

- [x] T021 [US3] Create `CHANGELOG.md` at repository root with Keep a Changelog header, format link, and Last Updated date (FR-003, FR-008)
- [x] T022 [US3] Add `[Unreleased]` section to `CHANGELOG.md` with entries for this documentation feature and MIT License (FR-003)
- [x] T023 [US3] Add `[0.2.0] - 2026-02-09` section to `CHANGELOG.md` documenting 002-hardware-component-api: Component base model, CPU/DRAM endpoints, general components endpoint, cross-endpoint visibility, field validation (FR-003)
- [x] T024 [US3] Add `[0.1.0] - 2026-02-06` section to `CHANGELOG.md` documenting 001-drf-docker-setup: Django 5.1 scaffolding, Docker Compose, dual DB support, debugpy, pytest config, entrypoint.sh (FR-003)

**Checkpoint**: Changelog complete — covers all features from project inception to current

---

## Phase 6: User Story 4 — Stakeholder Reviews Architecture (Priority: P4)

**Goal**: Technical lead or new developer understands system design, data model, and how to extend it.

**Independent Test**: Reader can explain the inheritance pattern and add a new component type after reading the doc.

### Implementation for User Story 4

- [x] T025 [US4] Create `docs/architecture.md` with title, Last Updated date, and system overview section describing cperf-api as a Django REST API for hardware component performance data (FR-004, FR-008)
- [x] T026 [US4] Add Technology Stack section to `docs/architecture.md` — Python 3.12, Django 5.1, DRF 3.15, PostgreSQL 16 (production/Docker), SQLite (local dev), django-environ, django-filter, Docker Compose (FR-004)
- [x] T027 [US4] Add Data Model section to `docs/architecture.md` with Mermaid class diagram showing Component (UUID id, name, component_type, description, created_at, updated_at) → CpuComponent (cores, threads, clock_speed, boost_clock, tdp, socket) and DramComponent (capacity_gb, speed_mhz, ddr_type, modules, cas_latency, voltage) multi-table inheritance (FR-004)
- [x] T028 [US4] Add API Design section to `docs/architecture.md` — RESTful pattern: read-only aggregate `/api/components/` + full CRUD per type (`/api/cpu/`, `/api/dram/`), ViewSets + DefaultRouter, PageNumberPagination (20/page), DjangoFilterBackend + SearchFilter + OrderingFilter (FR-004)
- [x] T029 [US4] Add "Adding a New Component Type" guide to `docs/architecture.md` — step-by-step: 1) `django-admin startapp`, 2) create model extending Component, 3) add serializer, 4) add ViewSet, 5) add urls.py with DefaultRouter, 6) register in INSTALLED_APPS, 7) include in config/urls.py, 8) makemigrations + migrate (FR-004)
- [x] T030 [US4] Add Environment Configuration section to `docs/architecture.md` — django-environ pattern, DATABASE_URL with SQLite fallback, .env/.env.example/.env.local files, Docker vs local env var differences (FR-004)

**Checkpoint**: Architecture doc complete — new developer can understand and extend the system

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final review and cross-document consistency

- [x] T031 Verify all "Last Updated: 2026-02-09" dates present in README.md, docs/api.md, CHANGELOG.md, docs/architecture.md (FR-008)
- [x] T032 Verify consistent terminology across all docs — "component type" (not "category"), "multi-table inheritance" (not "polymorphism"), endpoint paths match actual urls.py
- [x] T033 Verify README API Overview table links correctly to docs/api.md
- [x] T034 Run quickstart.md verification checklist from `specs/003-project-docs/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Already complete (doc-sync rules created)
- **US1 README (Phase 3)**: Depends on Phase 1 (docs/ dir exists); T013 references docs/api.md (write link, file created later)
- **US2 API Ref (Phase 4)**: Depends on Phase 1 (docs/ dir exists); independent of US1
- **US3 Changelog (Phase 5)**: No dependencies on other stories
- **US4 Architecture (Phase 6)**: Depends on Phase 1 (docs/ dir exists); independent of other stories
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (README)**: Can start after Phase 1 — no dependencies on US2/US3/US4
- **US2 (API Ref)**: Can start after Phase 1 — no dependencies on US1/US3/US4
- **US3 (Changelog)**: Can start after Phase 1 — no dependencies on other stories
- **US4 (Architecture)**: Can start after Phase 1 — no dependencies on other stories

### Parallel Opportunities

All four user stories write to different files and can execute in parallel:

```
Phase 1 (Setup)
    │
    ├──→ Phase 3: US1 (README.md)         ─┐
    ├──→ Phase 4: US2 (docs/api.md)        ├──→ Phase 7 (Polish)
    ├──→ Phase 5: US3 (CHANGELOG.md)       │
    └──→ Phase 6: US4 (docs/architecture.md)┘
```

Within each story, tasks are sequential (each builds on the previous section).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 3: User Story 1 — README.md (T005-T014)
3. **STOP and VALIDATE**: Follow the README from a fresh perspective
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Setup complete
2. US1 → README complete → developers can onboard
3. US2 → API reference complete → consumers can integrate
4. US3 → Changelog complete → team can track changes
5. US4 → Architecture doc complete → full documentation suite
6. Phase 7 → Polish and cross-check

### Parallel Execution (Recommended)

Since all user stories write to different files:

```
Launch in parallel:
  Agent 1: T005-T014 (README.md)
  Agent 2: T015-T020 (docs/api.md)
  Agent 3: T021-T024 (CHANGELOG.md)
  Agent 4: T025-T030 (docs/architecture.md)
```

---

## Notes

- No code changes — all tasks create or write documentation files
- All content must be derived from the actual codebase (models, views, serializers, Dockerfile, etc.)
- T003-T004 already completed during clarification phase
- Commit after each phase or user story completion
- Every doc must include "Last Updated: 2026-02-09"
