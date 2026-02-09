# Implementation Plan: Hardware Component API & Project Restructure

**Branch**: `002-hardware-component-api` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-hardware-component-api/spec.md`

## Summary

Restructure the cperf-api project from the placeholder `sample` app to a multi-app architecture for hardware components. A `components` app provides a shared base model and general read endpoint (`/api/components/`). Type-specific apps (`cpu`, `dram`) inherit from the base model via Django multi-table inheritance and provide full CRUD endpoints with type-specific fields. Container-mode test execution is added to docker-compose.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Django 5.1, Django REST Framework 3.15, django-environ, psycopg2-binary, debugpy
**Storage**: PostgreSQL 16 (container), SQLite 3 (local debug)
**Testing**: pytest with pytest-django
**Target Platform**: Linux containers (Docker), local Windows/macOS/Linux for debug
**Project Type**: Web (API backend only)
**Performance Goals**: Component queries < 1 second for 1,000 records
**Constraints**: No external ORM dependencies (no django-polymorphic); built-in Django multi-table inheritance only
**Scale/Scope**: Initial types: CPU, DRAM. Architecture supports adding more types without modifying existing apps.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is unpopulated (template placeholders only). No active gates to evaluate. Proceeding without violations.

**Post-Phase 1 re-check**: No violations. Multi-table inheritance is a built-in Django pattern. Three apps (components, cpu, dram) is appropriate for the domain separation.

## Project Structure

### Documentation (this feature)

```text
specs/002-hardware-component-api/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml     # OpenAPI 3.1 specification
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
cperf-api/
├── config/                      # Django project configuration (existing)
│   ├── __init__.py
│   ├── settings.py              # Updated: replace sample with new apps
│   ├── urls.py                  # Updated: new URL includes
│   ├── wsgi.py
│   └── asgi.py
├── components/                  # NEW: base component app
│   ├── __init__.py
│   ├── admin.py                 # Component admin registration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Component base model (concrete)
│   ├── serializers.py           # Base component serializer
│   ├── views.py                 # Read-only ViewSet for general queries
│   ├── urls.py                  # Router: /api/components/
│   └── migrations/
│       └── 0001_initial.py
├── cpu/                         # NEW: CPU component app
│   ├── __init__.py
│   ├── admin.py                 # CPU admin registration
│   ├── apps.py
│   ├── models.py                # CpuComponent (inherits Component)
│   ├── serializers.py           # CPU-specific serializer with validation
│   ├── views.py                 # Full CRUD ModelViewSet
│   ├── urls.py                  # Router: /api/cpu/
│   └── migrations/
│       └── 0001_initial.py
├── dram/                        # NEW: DRAM component app
│   ├── __init__.py
│   ├── admin.py                 # DRAM admin registration
│   ├── apps.py
│   ├── models.py                # DramComponent (inherits Component)
│   ├── serializers.py           # DRAM-specific serializer with validation
│   ├── views.py                 # Full CRUD ModelViewSet
│   ├── urls.py                  # Router: /api/dram/
│   └── migrations/
│       └── 0001_initial.py
├── tests/                       # Updated test suite
│   ├── __init__.py
│   ├── conftest.py              # Updated: component fixtures
│   ├── test_components_api.py   # NEW: general endpoint tests
│   ├── test_cpu_api.py          # NEW: CPU CRUD tests
│   └── test_dram_api.py         # NEW: DRAM CRUD tests
├── manage.py
├── Dockerfile
├── docker-compose.yml           # Updated: test profile added
├── entrypoint.sh
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── .env.example
├── pytest.ini
└── setup.cfg
```

**Structure Decision**: Multi-app Django layout. `components/` owns the base model and general read endpoint. `cpu/` and `dram/` are independent type-specific apps that inherit from the base model. Each app is self-contained with its own model, serializer, viewset, URLs, and migrations. The `sample/` app is fully removed.

## Key Design Decisions

### D-001: Django Multi-Table Inheritance (No External Dependencies)

The `Component` model in `components/` is a concrete Django model. `CpuComponent` and `DramComponent` in their respective apps inherit from `Component`, which Django implements as separate child tables linked by an automatic OneToOneField (`component_ptr`).

**Why not django-polymorphic**: The general endpoint only needs base fields (name, type, description). It queries the `components_component` table directly without JOINs. Type-specific endpoints query their own child tables (auto-JOINs to base). Since we don't need automatic subclass resolution on the general endpoint, the external dependency is unnecessary.

**Query behavior**:
- `Component.objects.all()` → queries base table only (no JOINs), returns base fields
- `CpuComponent.objects.all()` → queries cpu table + JOIN to base table, returns all fields
- Creating a `CpuComponent` → inserts into both tables (handled by Django automatically)

### D-002: Open Component Type Field

The `component_type` CharField on the base model is not constrained by `choices`. Each child model's `save()` method auto-sets it (e.g., `self.component_type = "cpu"`). This means:
- Adding a new type never requires changing the `components` app
- The general endpoint filters by type via query parameter
- Unknown types return empty results (not errors)

### D-003: General Endpoint is Read-Only

The `/api/components/` endpoint only supports `list` and `retrieve` actions (no create/update/delete). Components must be created via their type-specific endpoints to ensure proper child table records and type-specific validation. This prevents orphaned base records without child data.

### D-004: Container Test Execution

Tests run in the container via `docker compose run --rm web pytest`. This reuses the web service image, connects to the PostgreSQL database, and cleans up the container after execution. The entrypoint runs migrations before pytest starts, ensuring the test database schema is current.

## Complexity Tracking

No constitution violations to justify. The project uses standard Django patterns:
- Multi-table inheritance is built-in Django
- Three apps (components, cpu, dram) map directly to the domain
- No external dependencies added beyond what feature 001 established
