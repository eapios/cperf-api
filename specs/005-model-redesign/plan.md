# Implementation Plan: Backend Model Redesign

**Branch**: `005-model-redesign` | **Date**: 2026-02-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-model-redesign/spec.md`
**Design**: `docs/005-model-redesign/model-design.md`

## Summary

Replace the current multi-table inheritance model (Component → CpuComponent, DramComponent) with a flat, domain-specific model structure across 5 Django apps (properties, nand, cpu, dram, results). Introduces PropertyConfig/ConfigSet for frontend rendering, ExtendedProperty/ExtendedPropertyValue for user-defined computed columns with per-instance values, and ResultRecord/ResultInstance for saving calculation runs. All model definitions are specified in `docs/005-model-redesign/model-design.md`.

## Technical Context

**Language/Version**: Python 3.12 + Django 5.1
**Primary Dependencies**: Django REST Framework 3.15, django-environ, django-filter, psycopg2-binary
**Storage**: PostgreSQL 16 (Docker), SQLite 3 (local debug)
**Testing**: pytest + pytest-django
**Target Platform**: Linux server (Docker), Windows (local dev)
**Project Type**: Backend API (Django apps at repo root)
**Performance Goals**: Standard — low data volume, single-digit concurrent users
**Constraints**: Pre-production, no data migration needed
**Scale/Scope**: ~16 models across 5 apps, ~15 API endpoints, ~45 fields on largest model (Nand)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a blank template — no project-specific gates defined. **PASS** (no violations possible).

## Project Structure

### Documentation (this feature)

```text
specs/005-model-redesign/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Existing apps (to be replaced/redesigned)
components/              # DROP: old Component base model
cpu/                     # REPLACE: CpuComponent → Cpu
dram/                    # REPLACE: DramComponent → Dram

# New apps
properties/              # NEW: PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership,
│                        #      ExtendedPropertySet, ExtendedProperty, ExtendedPropertyValue, BaseEntity
│   ├── __init__.py
│   ├── base.py          # BaseEntity abstract model
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
nand/                    # NEW: Nand, NandInstance, NandPerf
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
results/                 # NEW: ResultProfile, ResultWorkload, ResultProfileWorkload,
│   ├── __init__.py      #      ResultRecord, ResultInstance
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py

# Redesigned apps
cpu/                     # REPLACE: Cpu with BaseEntity, bandwidth only
dram/                    # REPLACE: Dram with BaseEntity, bandwidth+channel+transfer_rate

# Tests
tests/
├── conftest.py
├── test_properties_api.py   # NEW
├── test_nand_api.py         # NEW
├── test_cpu_api.py          # REPLACE
├── test_dram_api.py         # REPLACE
├── test_results_api.py      # NEW
└── test_extended_props.py   # NEW (GenericFK, CHECK constraint, per-instance values)

# Config
config/
├── settings.py          # UPDATE: INSTALLED_APPS (remove components, add properties/nand/results)
└── urls.py              # UPDATE: new URL patterns
```

**Structure Decision**: Django apps at repo root (matching existing pattern). No `src/` directory — the project uses `manage.py` at root with apps as siblings. Old `components/` app is dropped entirely; `cpu/` and `dram/` are rewritten in-place; `properties/`, `nand/`, and `results/` are new apps.

## Complexity Tracking

No constitution violations — section not applicable.
