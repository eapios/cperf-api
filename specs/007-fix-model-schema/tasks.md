# Tasks: Model Schema Fixes

**Input**: Design documents from `/specs/007-fix-model-schema/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

---

## Phase 1: Baseline Check

**Purpose**: Confirm all existing tests pass before any changes. Establishes a known-good state.

- [x] T001 Run `pytest` and confirm zero failures as baseline

---

## Phase 2: User Story 1 — ResultRecord Simplification (Priority: P1) 🎯 MVP

**Goal**: Replace `ResultRecord` hardware FK columns with a single `data` JSONField; remove `ResultInstance` entirely.

**Independent Test**: `POST /api/result-records/` with `{"name": "run-001", "data": {"nand": {}}}` returns 201 with `data` field present and no `nand`/`cpu`/`dram` FK fields. `GET` on the same record returns identical shape.

### Implementation

- [x] T002 [US1] Update `results/models.py` — remove `ResultInstance` class; remove `nand`, `nand_instance`, `nand_perf`, `cpu`, `dram` FK fields from `ResultRecord`; add `data = models.JSONField(null=True, blank=True, default=None)`
- [x] T003 [US1] Create `results/migrations/0002_simplify_result_record.py` — `DeleteModel("ResultInstance")`, `RemoveField` for all 5 FK columns, `AddField` for `data` JSONField
- [x] T004 [P] [US1] Update `results/serializers.py` — remove `ResultInstanceSerializer`; update `ResultRecordSerializer.Meta.fields` to `["id", "name", "data", "created_at", "updated_at"]`
- [x] T005 [P] [US1] Update `results/views.py` — remove `ResultInstanceFilter` and `ResultInstanceViewSet`; remove all `ResultInstance` imports
- [x] T005a [P] [US1] Update `results/admin.py` — remove `ResultInstance` registration (and its import); this file is separate from views and easy to miss
- [x] T006 [P] [US1] Update `results/urls.py` — remove `result-instances` router registration and `ResultInstanceViewSet` import
- [x] T007 [P] [US1] Update `tests/test_results_api.py` — delete `TestResultInstance` class entirely; rewrite `TestResultRecord` to assert `data` field present, assert no `nand`/`cpu`/`dram` fields in response

**Checkpoint**: `pytest tests/test_results_api.py` passes; no `ResultInstance` references remain in `results/`

---

## Phase 3: User Story 2 — ExtendedProperty Set Membership (Priority: P2)

**Goal**: Introduce `ExtendedPropertySetMembership` junction table; remove `property_set` FK from `ExtendedProperty`; make `content_type` required.

**Independent Test**: Create two `ExtendedPropertySet`s and one `ExtendedProperty` (with `content_type` set). POST to `/api/extended-property-set-memberships/` twice — once per set. GET each set and confirm the same property appears in both `items` arrays.

### Implementation

- [x] T008 [US2] Update `properties/models.py`:
  - Add `ExtendedPropertySetMembership` model with `property_set` FK (CASCADE, `related_name="memberships"`), `extended_property` FK (CASCADE, `related_name="memberships"`), `index` PositiveIntegerField; `Meta.ordering=["index"]`; constraints `unique_extended_prop_in_set(property_set, extended_property)` and `unique_index_in_extended_set(property_set, index)`
  - Remove `property_set` FK field from `ExtendedProperty`
  - Change `ExtendedProperty.content_type` from `null=True, blank=True` to non-nullable (remove those kwargs)
  - Remove constraints `extended_prop_single_binding` and `unique_extended_prop_per_set`; simplify `unique_extended_prop_per_model_type` to unconditional `UniqueConstraint(fields=["content_type","name"])`
- [x] T009 [US2] Create `properties/migrations/0003_extended_property_set_membership.py` with steps:
  1. `CreateModel("ExtendedPropertySetMembership")` with all fields and constraints
  2. `RunPython` data migration — for each `ExtendedProperty` where `property_set_id IS NOT NULL`, create `ExtendedPropertySetMembership(property_set_id=ep.property_set_id, extended_property=ep, index=0)`
  3. `RunPython` cleanup — delete `ExtendedProperty` rows where `content_type_id IS NULL`
  4. `RemoveConstraint("ExtendedProperty", "extended_prop_single_binding")`
  5. `RemoveConstraint("ExtendedProperty", "unique_extended_prop_per_set")`
  6. `RemoveConstraint("ExtendedProperty", "unique_extended_prop_per_model_type")` ← **must come before step 9** (same constraint name reused; Django errors if name already exists)
  7. `RemoveField("ExtendedProperty", "property_set")`
  8. `AlterField("ExtendedProperty", "content_type")` — remove `null=True, blank=True`
  9. `AddConstraint("ExtendedProperty", UniqueConstraint(fields=["content_type","name"], name="unique_extended_prop_per_model_type"))` ← safe now that old constraint dropped in step 6
- [x] T010 [P] [US2] Update `properties/serializers.py`:
  - Add `ExtendedPropertySetMembershipSerializer` with nested `extended_property` (read-only `ExtendedPropertySerializer`) and write-only `extended_property_id` PrimaryKeyRelatedField; fields `["id", "index", "extended_property", "extended_property_id"]`
  - Update `ExtendedPropertySetSerializer` — add `items = ExtendedPropertySetMembershipSerializer(source="memberships", many=True, read_only=True)`; add `"items"` to Meta.fields
  - Update `ExtendedPropertySerializer` — remove `property_set` from Meta.fields; **delete `validate()` entirely** — DRF enforces non-nullable FK at field level automatically; no custom validation needed
- [x] T011 [P] [US2] Update `properties/views.py`:
  - Add `ExtendedPropertySetMembershipViewSet` — `ModelViewSet`, queryset `ExtendedPropertySetMembership.objects.select_related("property_set","extended_property").all()`, `http_method_names=["get","post","delete","head","options"]`
  - Update `ExtendedPropertySetViewSet.queryset` — add `.prefetch_related("memberships__extended_property")`
  - Update `ExtendedPropertyFilter` — remove `property_set` NumberFilter; add `set = django_filters.NumberFilter(method="filter_by_set")`; add `filter_by_set` method querying `memberships__property_set_id=value`
- [x] T012 [P] [US2] Update `properties/urls.py` — register `extended-property-set-memberships` with `ExtendedPropertySetMembershipViewSet`, `basename="extended-property-set-membership"`; add import
- [x] T013 [P] [US2] Update `properties/admin.py` — register `ExtendedPropertySetMembership`
- [x] T014 [P] [US2] Update `tests/test_extended_props.py`:
  - Rewrite `TestExtendedPropertyBinding` — remove "both bindings" and "neither binding" test cases; add test asserting `content_type` is required (POST without `content_type` → 400)
  - Rewrite `TestResultLevelPropertyResolve` — replace `property_set=eps` binding with `content_type=ResultWorkload CT` binding; verify resolve still works

**Checkpoint**: `pytest tests/test_extended_props.py` passes; `GET /api/extended-property-sets/{id}/` returns `items` array; same property can be in two sets

---

## Phase 4: User Story 3 — Documentation (Priority: P3)

**Goal**: Update architecture and API docs to reflect removed models, new membership table, and ExtendedProperty usage policy.

**Independent Test**: A developer reads the docs and finds a clear rule stating when to use `ExtendedProperty` vs a native model field, with one example each.

### Implementation

- [x] T015 [P] [US3] Update `docs/architecture.md` — data model section: remove `ResultInstance` entry, update `ResultRecord` (add `data` JSONField, remove FK fields), add `ExtendedPropertySetMembership` entity, update `ExtendedProperty` (content_type always required, property_set removed), add ExtendedProperty usage policy (static/formula only; variable per-instance data → native model field). Bump `Last Updated`.
- [x] T016 [P] [US3] Update `docs/api.md` — remove result-instances endpoint section, update ResultRecord request/response examples (add `data`, remove FK fields), add ExtendedPropertySetMembership endpoint section, update ExtendedProperty examples (remove property_set, add set filter), update ExtendedPropertySet response example (add items). Bump `Last Updated`.
- [x] T017 [P] [US3] Update `docs/models.ts` — remove `ResultInstance` interface; update `ResultRecord` (add `data: Record<string, unknown> | null`, remove FK fields); add `ExtendedPropertySetMembership` interface; update `ExtendedProperty` (remove `property_set`, make `content_type` non-optional); update `ExtendedPropertySet` (add `items`). Bump `Last Updated`.
- [x] T018 [P] [US3] Update `CHANGELOG.md` — add entries under `[Unreleased]`: removed ResultInstance model + endpoint, simplified ResultRecord (data JSONField), added ExtendedPropertySetMembership, made ExtendedProperty.content_type required, updated docs with usage policy

**Checkpoint**: All three docs updated and consistent with implementation

---

## Phase 5: Validation

**Purpose**: Full test suite + lint pass confirming all success criteria met.

- [x] T019 Run `python manage.py migrate` and confirm no errors
- [x] T020 [P] Run `pytest` — all tests pass, zero failures
- [x] T021 [P] Run `ruff check .` and `black .` — zero lint/format issues
- [x] T022 Grep codebase for `ResultInstance` references — confirm zero results outside migration files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Baseline)**: No dependencies — start immediately
- **Phase 2 (US1)**: Depends on Phase 1 completion
- **Phase 3 (US2)**: Depends on Phase 1; independent of Phase 2 (different apps)
- **Phase 4 (US3)**: Depends on Phase 2 and Phase 3 completion (docs describe final state)
- **Phase 5 (Validation)**: Depends on all prior phases

### User Story Dependencies

- **US1** and **US2** are independent — they touch different apps and can be done in either order or in parallel
- **US3** (docs) depends on US1 + US2 being implemented (describes final state)

### Within Each User Story

- Model changes first (T002 / T008)
- Migration second (T003 / T009) — depends on model
- Serializer, views, urls, admin, tests — all parallelizable after migration exists ([P] marked)

---

## Parallel Opportunities

### US1 — after T002 + T003 complete:
```
Task: "Update results/serializers.py (T004)"
Task: "Update results/views.py (T005)"
Task: "Update results/admin.py (T005a)"
Task: "Update results/urls.py (T006)"
Task: "Update tests/test_results_api.py (T007)"
```

### US2 — after T008 + T009 complete:
```
Task: "Update properties/serializers.py (T010)"
Task: "Update properties/views.py (T011)"
Task: "Update properties/urls.py (T012)"
Task: "Update properties/admin.py (T013)"
Task: "Update tests/test_extended_props.py (T014)"
```

### US3 — all four doc tasks are fully parallel:
```
Task: "Update docs/architecture.md (T015)"
Task: "Update docs/api.md (T016)"
Task: "Update docs/models.ts (T017)"
Task: "Update CHANGELOG.md (T018)"
```

---

## Implementation Strategy

### MVP (US1 only — 7 tasks)

1. T001 baseline check
2. T002 model changes
3. T003 migration
4. T004–T007 in parallel
5. Validate: `pytest tests/test_results_api.py`

### Full delivery order

1. Phase 1 → Phase 2 (US1) → Phase 3 (US2) → Phase 4 (US3) → Phase 5
2. Or: Phase 1 → Phase 2 + Phase 3 in parallel → Phase 4 → Phase 5
