# Implementation Plan: Model Schema Fixes

**Branch**: `007-fix-model-schema` | **Date**: 2026-03-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-fix-model-schema/spec.md`

## Summary

Simplify the result data model by replacing `ResultRecord` hardware FKs and the `ResultInstance` model with a single free-form JSON column. Fix the `ExtendedProperty` data model by replacing the direct `property_set` FK with an `ExtendedPropertySetMembership` junction table (mirrors `PropertyConfigSetMembership`), and enforce `content_type` as always-required.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Django 5.1, DRF 3.15, django-filter
**Storage**: SQLite (local dev), PostgreSQL 16 (Docker)
**Testing**: pytest
**Target Platform**: Linux server (Docker)
**Project Type**: Single Django project
**Performance Goals**: N/A (schema correction, no throughput change)
**Constraints**: Migrations must be reversible for dev; no production data to preserve
**Scale/Scope**: ~10 files changed across 2 apps

## Constitution Check

Constitution file is a blank template — no project-specific gates defined. Applying project CLAUDE.md principles:

| Principle | Status |
|---|---|
| KISS — no unnecessary abstraction | PASS — changes mirror existing patterns exactly |
| DRY — no duplication | PASS — membership table reuses same pattern as PropertyConfigSetMembership |
| YAGNI — no speculative features | PASS — changes are strictly what spec requires |

## Project Structure

### Documentation (this feature)

```text
specs/007-fix-model-schema/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   ├── result-records.md
│   └── extended-properties.md
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code

```text
results/
├── models.py            ← remove ResultInstance, strip FK fields, add data JSONField
├── serializers.py       ← remove ResultInstanceSerializer, update ResultRecordSerializer
├── views.py             ← remove ResultInstanceFilter + ResultInstanceViewSet
├── urls.py              ← remove result-instances registration
└── migrations/
    └── 0002_simplify_result_record.py  ← new

properties/
├── models.py            ← add ExtendedPropertySetMembership, modify ExtendedProperty
├── serializers.py       ← add membership serializer, update set + property serializers
├── views.py             ← add membership viewset, update ExtendedPropertyFilter
├── urls.py              ← register extended-property-set-memberships
├── admin.py             ← register ExtendedPropertySetMembership
└── migrations/
    └── 0003_extended_property_set_membership.py  ← new

tests/
├── test_results_api.py  ← delete TestResultInstance, rewrite TestResultRecord
└── test_extended_props.py  ← rewrite binding + result-level tests

docs/
├── architecture.md      ← update data model section
├── api.md               ← update affected endpoint sections
└── models.ts            ← update TypeScript interfaces

CHANGELOG.md             ← add unreleased entries
```

**Structure Decision**: Single Django project. Changes confined to `results/` and `properties/` apps plus test and doc files.

## Implementation Phases

### Phase A — Results app (P1, FR-001 to FR-004)

1. Update `results/models.py` — remove `ResultInstance`, remove FK fields, add `data` JSONField
2. Create `results/migrations/0002_simplify_result_record.py`
3. Update `results/serializers.py` — remove `ResultInstanceSerializer`, update `ResultRecordSerializer`
4. Update `results/views.py` — remove `ResultInstanceFilter` + `ResultInstanceViewSet`
5. Update `results/urls.py` — remove `result-instances` router entry
6. Update tests — delete `TestResultInstance`, rewrite `TestResultRecord`

### Phase B — Properties app (P2, FR-005 to FR-008)

1. Update `properties/models.py` — add `ExtendedPropertySetMembership`, modify `ExtendedProperty`
2. Create `properties/migrations/0003_extended_property_set_membership.py` (with data migration)
3. Update `properties/serializers.py` — add `ExtendedPropertySetMembershipSerializer`, update `ExtendedPropertySetSerializer` (add `items`), update `ExtendedPropertySerializer` (remove `property_set`, update validate)
4. Update `properties/views.py` — add `ExtendedPropertySetMembershipViewSet`, update `ExtendedPropertyFilter`
5. Update `properties/urls.py` — register membership endpoint
6. Update `properties/admin.py` — register `ExtendedPropertySetMembership`
7. Update tests — rewrite `TestExtendedPropertyBinding`, rewrite `TestResultLevelPropertyResolve`

### Phase C — Documentation (P3, FR-009, FR-010)

1. Update `docs/architecture.md` — removed models, new membership table, ExtendedProperty usage policy
2. Update `docs/api.md` — changed + removed endpoints
3. Update `docs/models.ts` — TypeScript interfaces
4. Update `CHANGELOG.md`
