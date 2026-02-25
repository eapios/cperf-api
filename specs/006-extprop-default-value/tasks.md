# Tasks: Extended Property Default Value

**Input**: Design documents from `/specs/006-extprop-default-value/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no cross-dependency)
- **[Story]**: Which user story this task belongs to
- Exact file paths in all descriptions

---

## Phase 1: Setup

**No new setup required.** The project, app (`properties/`), router, and test suite already exist. Proceed directly to Phase 2.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the `default_value` field to the model and generate the migration. Nothing in Phases 3–5 can be tested until this is done.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T001 Add `default_value = models.JSONField(null=True, blank=True, default=None)` to `ExtendedProperty` in `properties/models.py`
- [X] T002 Run `python manage.py makemigrations properties --name extendedproperty_default_value` to generate `properties/migrations/0002_extendedproperty_default_value.py`

**Checkpoint**: `ExtendedProperty.default_value` exists in Python and in the DB schema. Ready to implement user stories.

---

## Phase 3: User Story 1 — Define a Default Value (Priority: P1) 🎯 MVP

**Goal**: Clients can set `default_value` on an `ExtendedProperty` via the standard CRUD interface, and a single `resolve` call returns the default for instances with no per-instance record.

**Independent Test**: Create an `ExtendedProperty` with `default_value=65`. Call `GET /api/properties/extended-properties/{id}/resolve/?model=cpu&object_id=999` for an instance with no `ExtendedPropertyValue`. Verify response is `{"property_id": ..., "value": 65, "is_default": true}`.

### Implementation for User Story 1

- [X] T003 [P] [US1] Add `"default_value"` to `ExtendedPropertySerializer.Meta.fields` in `properties/serializers.py`
- [X] T004 [P] [US1] Add `resolve` `@action` to `ExtendedPropertyViewSet` in `properties/views.py`: `GET /{id}/resolve/?model=<app_label>&object_id=<pk>[&model_name=<model>]` — lookup ContentType via `ContentType.objects.get(app_label=model)` when `model_name` omitted, or `ContentType.objects.get(app_label=model, model=model_name)` when provided; returns `{"property_id", "value", "is_default"}`; 400 on missing params or MultipleObjectsReturned; 404 on unknown model

### Tests for User Story 1

- [X] T005 [P] [US1] Write test: `POST /api/properties/extended-properties/` with `default_value=65` persists field; `GET` returns `default_value: 65` — in `tests/test_extended_props.py`
- [X] T006 [P] [US1] Write test: `PATCH /{id}/` with `{"default_value": 0}` updates field; re-read confirms change — in `tests/test_extended_props.py`
- [X] T007 [US1] Write test: `resolve` returns `{"value": 65, "is_default": true}` when no `ExtendedPropertyValue` exists for instance — in `tests/test_extended_props.py`
- [X] T008 [US1] Write test: `resolve` returns `{"value": null, "is_default": true}` when `default_value=null` and no per-instance record — in `tests/test_extended_props.py`
- [X] T009 [US1] Write test: `resolve` returns `400` when `model` or `object_id` query param is missing — in `tests/test_extended_props.py`
- [X] T010 [US1] Write test: `resolve` returns `404` when `model=<nonexistent_app>` — in `tests/test_extended_props.py`

**Checkpoint**: US1 fully functional. `default_value` is settable, readable, and returned as fallback by `resolve`.

---

## Phase 4: User Story 2 — Per-Instance Value Takes Precedence (Priority: P2)

**Goal**: Verify (no new implementation) that a recorded `ExtendedPropertyValue` overrides `default_value` in the `resolve` response.

**Independent Test**: Create `ExtendedProperty(default_value=0)`. Add `ExtendedPropertyValue(value=125)` for instance A. Call `resolve` for A → `{"value": 125, "is_default": false}`. Call `resolve` for instance B (no record) → `{"value": 0, "is_default": true}`.

### Tests for User Story 2

- [X] T011 [US2] Write test: `resolve` for an instance that has a per-instance value returns `{"value": 125, "is_default": false}` (not the default 0) — in `tests/test_extended_props.py`
- [X] T012 [US2] Write test: same property, different instance with no record returns `{"value": 0, "is_default": true}` — in `tests/test_extended_props.py`
- [X] T013 [US2] Write test: updating `default_value` on the property does not affect existing `ExtendedPropertyValue` records; resolve for the recorded instance still returns its specific value — in `tests/test_extended_props.py`

**Checkpoint**: US2 confirmed. Override precedence works correctly with zero new implementation.

---

## Phase 5: User Story 3 — Formula Properties Support Default Value (Priority: P3)

**Goal**: Verify (no new implementation) that `is_formula=True` properties accept and return a formula string as `default_value`.

**Independent Test**: Create `ExtendedProperty(is_formula=True, default_value="A / B")`. Call `resolve` for an instance with no record → `{"value": "A / B", "is_default": true}`.

### Tests for User Story 3

- [X] T014 [US3] Write test: `ExtendedProperty(is_formula=True, default_value="A / B")` — `resolve` for instance with no record returns `{"value": "A / B", "is_default": true}` — in `tests/test_extended_props.py`
- [X] T015 [US3] Write test: formula property with `default_value=null` — `resolve` returns `{"value": null, "is_default": true}` — in `tests/test_extended_props.py`
- [X] T021 [US1/FR-005] Write test: resolve for a **result-level** `ExtendedProperty` (bound via `property_set`) with `default_value="result-default"` — call `GET /{id}/resolve/?model=<results-app>&model_name=<result-model>&object_id=999` for an instance with no `ExtendedPropertyValue`; verify response is `{"value": "result-default", "is_default": true}` — in `tests/test_extended_props.py`

**Checkpoint**: US3 confirmed + FR-005 (result-level) verified. Formula and non-formula properties, entity-level and result-level, all behave identically for `default_value`.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T016 [P] Update `docs/api.md` — add `default_value` to ExtendedProperty request/response examples; document `GET /{id}/resolve/` endpoint with params and response shape; bump `Last Updated`
- [X] T017 [P] Update `docs/architecture.md` — add `default_value` column to ExtendedProperty table in data model section; bump `Last Updated`
- [X] T018 [P] Update `docs/models.ts` — add `defaultValue: unknown | null` to `ExtendedProperty` interface
- [X] T019 Update `CHANGELOG.md` — add entry under `[Unreleased]`: `feat: add default_value to ExtendedProperty with resolve endpoint`
- [X] T020 Run full test suite (`pytest`) and confirm no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — start immediately
- **US1 (Phase 3)**: Requires Phase 2 complete (T001+T002)
- **US2 (Phase 4)**: Requires Phase 3 complete (resolve action + T007/T011 fixture pattern)
- **US3 (Phase 5)**: Requires Phase 3 complete (same resolve action)
- **Polish (Phase 6)**: Requires all desired stories complete

### Within Phase 3

- T003 and T004 are parallel (serializer vs. views — different files)
- T005 and T006 are parallel (both CRUD tests, independent fixtures)
- T007–T010 depend on T003+T004 being done

### Parallel Opportunities

Within Phase 3 after T003+T004 complete:
```
Task: T005 — CRUD test: POST default_value
Task: T006 — CRUD test: PATCH default_value
Task: T007 — resolve test: returns default
Task: T008 — resolve test: null default
```
(All touch the same file but test different scenarios — review for conflicts before parallelising.)

Within Phase 6 (all independent files):
```
Task: T016 — docs/api.md
Task: T017 — docs/architecture.md
Task: T018 — docs/models.ts
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Phase 2: T001 → T002 (model + migration)
2. Phase 3: T003 + T004 in parallel → T005–T010 (serializer, resolve, tests)
3. **STOP and VALIDATE**: `pytest tests/test_extended_props.py -v`
4. If green: proceed to US2/US3; otherwise fix before continuing

### Incremental Delivery

1. Phase 2 → Phase 3 → demo `default_value` CRUD + `resolve` (MVP)
2. Phase 4 → confirm override logic (no new code, test-only)
3. Phase 5 → confirm formula support (no new code, test-only)
4. Phase 6 → docs + changelog

### Total: 21 tasks

| Phase | Tasks | Parallel opportunities |
|---|---|---|
| Foundational | T001–T002 | 0 |
| US1 (P1) | T003–T010 | T003+T004 parallel; T005+T006 parallel |
| US2 (P2) | T011–T013 | 0 (sequential test scenarios) |
| US3 (P3) | T014–T015, T021 | T014+T015+T021 parallel |
| Polish | T016–T020 | T016+T017+T018 parallel |
