# Implementation Plan: Extended Property Default Value

**Branch**: `006-extprop-default-value` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)

## Summary

Add a `default_value` JSONField to `ExtendedProperty` so that instances without a per-instance `ExtendedPropertyValue` automatically receive a fallback. A new `resolve` action on the property viewset returns the effective value (per-instance or default) in a single API call, satisfying SC-002.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Django 5.1, DRF 3.15, django-filter
**Storage**: SQLite (local) / PostgreSQL 16 (Docker) — JSONField supported on both
**Testing**: pytest (pytest.ini configured)
**Target Platform**: Linux server (Docker) / Windows local (SQLite)
**Project Type**: Web API (Django REST Framework)
**Performance Goals**: N/A — single-row lookup per resolve call
**Constraints**: Existing migration chain must be preserved; no data backfill
**Scale/Scope**: Minimal — 1 new model field, 1 new API action, ~40 lines of code

## Constitution Check

Constitution is a blank template — no ratified constraints. Evaluated against CLAUDE.md and project conventions:

| Gate | Status | Notes |
|---|---|---|
| KISS | PASS | Smallest model change (1 field); no new models or apps |
| DRY | PASS | Resolution logic centralised in one view action |
| YAGNI | PASS | No speculative fields or extension points |
| Migrations safe | PASS | `null=True` field — no data migration needed |
| Tests required | PASS | Existing `test_extended_props.py` extended; TDD approach |
| Doc sync | PASS | api.md, architecture.md, models.ts, CHANGELOG.md planned |

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-extprop-default-value/
├── plan.md          ✓ (this file)
├── research.md      ✓ Phase 0 — all decisions resolved
├── data-model.md    ✓ Phase 1 — model changes
├── quickstart.md    ✓ Phase 1 — implementation guide
├── contracts/
│   └── extended-property.yaml  ✓ Phase 1 — OpenAPI contract
└── tasks.md         (Phase 2 — /speckit.tasks command)
```

### Source Code (repository root)

```text
properties/
├── models.py              ← add default_value to ExtendedProperty
├── serializers.py         ← add default_value to ExtendedPropertySerializer.fields
├── views.py               ← add resolve action to ExtendedPropertyViewSet
└── migrations/
    └── 0002_extendedproperty_default_value.py   ← new

tests/
└── test_extended_props.py ← extend with default_value scenarios

docs/
├── api.md                 ← document default_value field + resolve endpoint
├── architecture.md        ← update ExtendedProperty table
└── models.ts              ← add defaultValue?: any | null to interface
CHANGELOG.md               ← add [Unreleased] entry
```

**Structure Decision**: Single Django project (existing layout). No new apps, no new routers — the `resolve` action is registered automatically by the existing `DefaultRouter` for `ExtendedPropertyViewSet`.

## Implementation Phases

### Phase A — Model + Migration (foundation)

1. Add `default_value = models.JSONField(null=True, blank=True, default=None)` to `ExtendedProperty`
2. Run `python manage.py makemigrations properties --name extendedproperty_default_value`
3. Verify migration file matches expected `AddField` operation

### Phase B — Serializer + CRUD tests (TDD: RED → GREEN)

4. Write tests: `default_value` returned in GET, settable via POST/PATCH
5. Add `"default_value"` to `ExtendedPropertySerializer.Meta.fields`
6. Run tests — GREEN

### Phase C — Resolve action + tests (TDD: RED → GREEN)

7. Write tests for `resolve` endpoint (all acceptance scenarios from spec)
8. Add `resolve` `@action` to `ExtendedPropertyViewSet`
9. Import `ExtendedPropertyValue` in views.py (already imported via serializers — check)
10. Run tests — GREEN

### Phase D — Docs + Changelog

11. Update `docs/api.md` — new field and `/resolve/` endpoint
12. Update `docs/architecture.md` — ExtendedProperty table
13. Update `docs/models.ts` — `defaultValue?: unknown`
14. Update `CHANGELOG.md` under `[Unreleased]`

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Field type | `JSONField(null=True)` | Same type as `ExtendedPropertyValue.value`; null = "no default" |
| Resolution API | `GET /extended-properties/{id}/resolve/?model=&object_id=` | Single call satisfies SC-002; action on existing viewset |
| Formula support | No special handling | Spec: store and return as-is, same as per-instance values |
| Migration | `AddField` only, no backfill | Spec: existing rows get `null` |

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| JSONField behaves differently on SQLite vs PostgreSQL | Low | `models.JSONField` normalised by Django since 3.1 |
| `resolve` action conflicts with router URL | Low | DRF DefaultRouter appends `{pk}/resolve/` automatically |
| Regression in existing value tests | Low | Only additive changes; existing serializer fields unchanged |
