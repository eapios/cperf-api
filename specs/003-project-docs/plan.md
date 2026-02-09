# Implementation Plan: Project Documentation Suite

**Branch**: `003-project-docs` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-project-docs/spec.md`

## Summary

Create five documentation files for the cperf-api project: README.md (developer onboarding with local/Docker/debug/test workflows), docs/api.md (complete API endpoint reference), CHANGELOG.md (Keep a Changelog format), docs/architecture.md (system design overview), and LICENSE (MIT). All content is derived from the existing codebase — no code changes required.

## Technical Context

**Language/Version**: N/A (documentation-only feature)
**Primary Dependencies**: N/A
**Storage**: N/A
**Testing**: Manual review — verify documented commands work against running server
**Target Platform**: Markdown files rendered on GitHub / local editors
**Project Type**: Documentation
**Performance Goals**: N/A
**Constraints**: Must accurately reflect current codebase state (branch 002-hardware-component-api)
**Scale/Scope**: 5 files, ~500-800 total lines of documentation

## Constitution Check

*GATE: Constitution is not configured (template only). No gates to enforce. Proceeding.*

## Project Structure

### Documentation (this feature)

```text
specs/003-project-docs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Files to create (all at repo root or docs/)
README.md                # FR-001: Developer onboarding guide
LICENSE                  # FR-009: MIT License
CHANGELOG.md             # FR-003: Change history
docs/
├── api.md               # FR-002: API endpoint reference
└── architecture.md      # FR-004: System design overview
```

**Structure Decision**: All documentation lives at repo root or under `docs/`. This follows standard open-source project conventions. No code changes needed.

## Implementation Phases

### Phase 1: LICENSE file (FR-009)

Create `LICENSE` at repo root with MIT License text, copyright year 2026, copyright holder from git config or project name.

**Deliverable**: `LICENSE`

### Phase 2: README.md (FR-001, FR-005, FR-006)

Create comprehensive `README.md` with these sections:

1. **Project Overview** — What cperf-api is (hardware component performance API)
2. **Prerequisites** — Python 3.12, Docker/Docker Compose (optional), Git
3. **Quick Start (Local)** — venv setup, pip install, SQLite migrations, runserver
4. **Quick Start (Docker)** — docker compose up, verify at localhost:8000
5. **Running Tests** — pytest command, coverage
6. **Debugging** — debugpy setup for both local and Docker modes (VS Code launch.json, PyCharm config)
7. **Project Structure** — Directory tree with descriptions
8. **API Overview** — Brief endpoint summary linking to docs/api.md
9. **License** — MIT reference

Key details to document:
- Local mode uses SQLite (no DATABASE_URL needed), Docker mode uses PostgreSQL
- `.env.example` should be copied to `.env` for Docker
- debugpy is in dev requirements, attach on port 5678
- pytest.ini is preconfigured, just run `pytest`

**Deliverable**: `README.md`

### Phase 3: API Reference (FR-002, FR-007)

Create `docs/api.md` documenting all endpoints:

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/components/` | GET | List all components (read-only, paginated) |
| `/api/components/{id}/` | GET | Retrieve single component by UUID |
| `/api/cpu/` | GET, POST | List / Create CPU components |
| `/api/cpu/{id}/` | GET, PUT, PATCH, DELETE | CRUD single CPU |
| `/api/dram/` | GET, POST | List / Create DRAM components |
| `/api/dram/{id}/` | GET, PUT, PATCH, DELETE | CRUD single DRAM |

For each endpoint, document:
- HTTP method + URL
- Query parameters (search, ordering, component_type filter)
- Request body (for POST/PUT/PATCH) with field types and constraints
- Response body with example JSON
- Status codes
- curl examples

**Deliverable**: `docs/api.md`

### Phase 4: CHANGELOG.md (FR-003)

Create `CHANGELOG.md` in Keep a Changelog format:

```
# Changelog

## [Unreleased]

### Added
- Project documentation suite (README, API reference, architecture docs, changelog)
- MIT License

## [0.2.0] - 2026-02-09

### Added
- Hardware component API with Component base model (UUID, name, type, description)
- CPU endpoint (/api/cpu/) with full CRUD, cores/threads/clock_speed/boost_clock/tdp/socket fields
- DRAM endpoint (/api/dram/) with full CRUD, capacity_gb/speed_mhz/ddr_type/modules/cas_latency/voltage fields
- Read-only general components endpoint (/api/components/) with filtering, search, ordering
- Cross-endpoint visibility (components created via type endpoints appear in general listing)
- Field validation (threads >= cores, boost_clock >= clock_speed for CPU)

## [0.1.0] - 2026-02-06

### Added
- Django 5.1 project scaffolding with DRF 3.15
- Docker Compose setup with PostgreSQL 16 and Django dev server
- Dual database support: SQLite (local) / PostgreSQL (Docker)
- debugpy integration for remote debugging
- pytest + pytest-django test configuration
- entrypoint.sh with PostgreSQL readiness check and auto-migration
```

**Deliverable**: `CHANGELOG.md`

### Phase 5: Architecture Document (FR-004)

Create `docs/architecture.md` with:

1. **System Overview** — Django REST API for hardware component performance data
2. **Technology Stack** — Python 3.12, Django 5.1, DRF 3.15, PostgreSQL 16 / SQLite, Docker
3. **Data Model** — Mermaid diagram showing Component base → CpuComponent / DramComponent multi-table inheritance, with field listings
4. **API Design** — RESTful pattern: read-only aggregate endpoint + full CRUD per component type. ViewSets + DefaultRouter. PageNumberPagination (20/page). DjangoFilterBackend + SearchFilter + OrderingFilter.
5. **Adding a New Component Type** — Step-by-step guide: create app, extend Component model, add serializer/viewset/urls, register in settings and root urls
6. **Environment Configuration** — django-environ, DATABASE_URL pattern, .env files

**Deliverable**: `docs/architecture.md`

## Cross-Cutting Concerns

- **FR-008**: Every document includes a "Last Updated: YYYY-MM-DD" line
- **Accuracy**: All commands, URLs, field names, and examples must match the actual codebase
- **Consistency**: Use the same terminology across all docs (e.g., "component type" not "category")

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docs become stale after code changes | Developers follow wrong instructions | "Last Updated" dates flag staleness; architecture doc includes "Adding a New Component" guide |
| debugpy instructions vary by IDE | Some developers can't debug | Cover both VS Code and PyCharm; link to debugpy official docs |
| Curl examples use wrong field names | API consumers get errors | Derive all examples from actual serializer fields and running tests |
