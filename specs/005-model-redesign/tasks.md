# Tasks: Backend Model Redesign

**Input**: Design documents from `specs/005-model-redesign/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api-endpoints.md ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Exact file paths included in all task descriptions

## Path Conventions

Django apps at repo root (no `src/` directory). `manage.py` at root, apps as siblings.

---

## Phase 1: Setup (App Scaffolding)

**Purpose**: Remove old apps, scaffold new app directories.

- [X] T001 [P] Remove `components/` app directory entirely (delete all files)
- [X] T002 [P] Remove `sample/` app directory entirely (delete all files)
- [X] T003 [P] Create `properties/` Django app scaffold: `properties/__init__.py`, `properties/apps.py`, `properties/base.py`, `properties/models.py`, `properties/serializers.py`, `properties/views.py`, `properties/urls.py`, `properties/admin.py`
- [X] T004 [P] Create `nand/` Django app scaffold: `nand/__init__.py`, `nand/apps.py`, `nand/models.py`, `nand/serializers.py`, `nand/views.py`, `nand/urls.py`, `nand/admin.py`
- [X] T005 [P] Create `results/` Django app scaffold: `results/__init__.py`, `results/apps.py`, `results/models.py`, `results/serializers.py`, `results/views.py`, `results/urls.py`, `results/admin.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Write `BaseEntity` abstract model (`name: CharField`, `created_at`, `updated_at` auto-timestamps) in `properties/base.py`
- [X] T007 Update `config/settings.py`: remove `components` and `sample` from `INSTALLED_APPS`, add `properties`, `nand`, `results`; verify `django.contrib.contenttypes` is present
- [X] T008 [P] Clear old migration files: delete all files in `cpu/migrations/` and `dram/migrations/` except `__init__.py` (enables clean migration without old Component base class)
- [X] T009 [P] Create `tests/conftest.py` with pytest-django `db` and `api_client` (`APIClient`) fixtures

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 — Migrate to New Model Structure (Priority: P1) 🎯 MVP

**Goal**: All 15 new tables created with correct schema, constraints, and indexes. Old Component/CpuComponent/DramComponent tables removed.

**Independent Test**: Run `python manage.py showmigrations` and verify all applied; run `python manage.py shell -c "from nand.models import Nand; from results.models import ResultRecord; print('OK')"` without errors.

### Implementation for User Story 1

- [X] T010 [P] [US1] Write `Cpu` model (inherits `BaseEntity`, adds `bandwidth: FloatField`) in `cpu/models.py`; update `cpu/apps.py`
- [X] T011 [P] [US1] Write `Dram` model (inherits `BaseEntity`, adds `bandwidth: FloatField`, `channel: IntegerField`, `transfer_rate: FloatField`) in `dram/models.py`; update `dram/apps.py`
- [X] T012 [P] [US1] Write `Nand`, `NandInstance`, `NandPerf` models in `nand/models.py`: `Nand` with ~45 flat fields grouped physically/endurance/raid/mapping/firmware/journal (with `MaxValueValidator(1.0)` on ratio fields, `JSONField` for `pb_per_disk_by_channel`); `NandInstance` with `UNIQUE(nand, name)`; `NandPerf` with `bandwidth`, `channel`, `die_per_channel`; update `nand/apps.py`
- [X] T013 [P] [US1] Write `PropertyConfig`, `PropertyConfigSet`, `PropertyConfigSetMembership` models in `properties/models.py`: `PropertyConfig(content_type FK, name, display_text, unit, decimal_places, ...)` with `UNIQUE(content_type, name)`; `PropertyConfigSet` with `UNIQUE(content_type, name)`; `PropertyConfigSetMembership(config_set, config, index)` with `UNIQUE(set, config)` and `UNIQUE(set, index)`
- [X] T014 [US1] Write `ExtendedPropertySet`, `ExtendedProperty`, `ExtendedPropertyValue` models in `properties/models.py` (after T013 — same file): `ExtendedPropertySet(name, content_type nullable)`; `ExtendedProperty(content_type OR property_set, name, is_formula)` with partial unique indexes and CHECK constraint (exactly one binding); `ExtendedPropertyValue(extended_property, content_type FK, object_id, value)` with `GenericForeignKey`, `UNIQUE(property, content_type, object_id)`, and composite index on `(content_type, object_id)`
- [X] T015 [P] [US1] Write `ResultProfile`, `ResultWorkload`, `ResultProfileWorkload`, `ResultRecord`, `ResultInstance` models in `results/models.py`: use string FK references (`"nand.Nand"`) for cross-app FKs; `ResultRecord` with nullable `SET_NULL` FKs to all hardware models and `-created_at` ordering; `ResultInstance` with `UNIQUE(result_record, profile_workload)`; `ResultProfileWorkload` with `UNIQUE(profile, workload)`; update `results/apps.py`
- [X] T016 [P] [US1] Register all models in admin: `cpu/admin.py` (Cpu), `dram/admin.py` (Dram), `nand/admin.py` (Nand, NandInstance, NandPerf), `properties/admin.py` (PropertyConfig, PropertyConfigSet, ExtendedProperty, ExtendedPropertyValue), `results/admin.py` (ResultProfile, ResultWorkload, ResultProfileWorkload, ResultRecord, ResultInstance)
- [X] T017 [US1] Generate migrations for all apps: `python manage.py makemigrations properties nand cpu dram results` — inspect generated files and confirm 15 tables will be created
- [X] T018 [US1] Apply migrations: `python manage.py migrate` — verify via `python manage.py showmigrations` that all migrations are applied and old Component tables are absent

**Checkpoint**: US1 complete — all 15 tables exist, schema matches `data-model.md`.

---

## Phase 4: User Story 2 — CRUD Hardware Components (Priority: P1)

**Goal**: Full CRUD API endpoints for Nand, NandInstance, NandPerf, Cpu, and Dram with field validation enforced.

**Independent Test**: POST/GET/PATCH/DELETE each component type via `/api/nand/`, `/api/cpu/`, `/api/dram/`, `/api/nand-instances/`, `/api/nand-perf/`. Verify 201 on create, 400 on ratio > 1.0, 204 on delete with cascade.

### Implementation for User Story 2

- [X] T019 [P] [US2] Write `CpuSerializer` (ModelSerializer, all BaseEntity fields + bandwidth) in `cpu/serializers.py`; write `CpuViewSet` (ModelViewSet) in `cpu/views.py`
- [X] T020 [P] [US2] Write `DramSerializer` (ModelSerializer, all BaseEntity fields + bandwidth/channel/transfer_rate) in `dram/serializers.py`; write `DramViewSet` (ModelViewSet) in `dram/views.py`
- [X] T021 [P] [US2] Write `NandSerializer` in `nand/serializers.py` with nested read groups — use nested serializer classes (one per group) to map flat model fields into 6 response groups: `physical`, `endurance`, `raid`, `mapping`, `firmware`, `journal`, plus `pb_per_disk_by_channel`; write operations (POST/PUT/PATCH) accept **flat field names** — nesting is response-only
- [X] T022 [US2] Write `NandInstanceSerializer` and `NandPerfSerializer` in `nand/serializers.py` (same file as T021 — sequential)
- [X] T023 [US2] Write `NandViewSet`, `NandInstanceViewSet` (with `django_filters` or manual `get_queryset` for `?nand=N`), `NandPerfViewSet` (with `?nand=N` filter) in `nand/views.py`
- [X] T024 [P] [US2] Write DefaultRouter URL registrations in `nand/urls.py` (`nand/`, `nand-instances/`, `nand-perf/`), `cpu/urls.py` (`cpu/`), `dram/urls.py` (`dram/`)
- [X] T025 [US2] Update `config/urls.py`: include `nand.urls`, `cpu.urls`, `dram.urls` under `/api/` prefix; remove any remaining old `components` or `sample` URL includes

### Tests for User Story 2

- [X] T026 [P] [US2] Write Nand API tests in `tests/test_nand_api.py`: CRUD lifecycle, `UNIQUE(nand, name)` on NandInstance, cascade delete, `MaxValueValidator` rejection on ratio fields > 1.0, `?nand=N` filter on list endpoints
- [X] T027 [P] [US2] Write CPU and DRAM API tests in `tests/test_cpu_api.py` and `tests/test_dram_api.py`: CRUD lifecycle, `updated_at` refresh on PATCH, 400 on missing required fields

**Checkpoint**: US2 complete — all hardware CRUD works independently, tests pass.

---

## Phase 5: User Story 3 — Manage Property Configs and Config Sets (Priority: P2)

**Goal**: CRUD endpoints for PropertyConfig and PropertyConfigSet; ordered membership enforced; `?config_set=<id>` query param on all entity detail endpoints.

**Independent Test**: Create PropertyConfigs for Nand type, create PropertyConfigSet, add memberships with indices. GET `/api/config-sets/{id}/` returns ordered items. GET `/api/nand/{id}/?config_set={id}` includes config set data; without param it is omitted.

### Implementation for User Story 3

- [X] T028 [P] [US3] Write `PropertyConfigSerializer`, `PropertyConfigSetMembershipSerializer` (with `config` nested), and `PropertyConfigSetSerializer` (with `items` nested, ordered by index) in `properties/serializers.py`
- [X] T029 [US3] Write `PropertyConfigViewSet` (with `?model=<app_label>` filter mapping to content_type) and `PropertyConfigSetViewSet` in `properties/views.py`
- [X] T030 [US3] Add `property-configs/` and `config-sets/` URL registrations to `properties/urls.py`
- [X] T031 [US3] Update `config/urls.py` to include `properties.urls` under `/api/` prefix
- [X] T032 [US3] Add `?config_set=<id>` query parameter support to `NandSerializer`, `NandInstanceSerializer`, `NandPerfSerializer`, `CpuSerializer`, `DramSerializer`: add a `config_set` `SerializerMethodField` that returns the ordered config set data when the query param is present, otherwise `None` (field omitted)

### Tests for User Story 3

- [X] T033 [US3] Write PropertyConfig and PropertyConfigSet API tests in `tests/test_properties_api.py`: `UNIQUE(content_type, name)` enforcement, `UNIQUE(set, config)` and `UNIQUE(set, index)` enforcement, ordered membership retrieval, `?config_set=<id>` included vs omitted in entity responses

**Checkpoint**: US3 complete — config sets work independently, entity detail responses include/omit configs correctly.

---

## Phase 6: User Story 4 — Define Extended Properties and Per-Instance Values (Priority: P2)

**Goal**: CRUD endpoints for ExtendedProperty definitions and ExtendedPropertyValue per-instance values; `?include=extended_properties` query param on entity detail endpoints.

**Independent Test**: Create ExtendedProperty for Nand type. Set ExtendedPropertyValues for two different Nand instances. GET `/api/nand/{id1}/?include=extended_properties` returns only instance 1's values; same for instance 2. Attempt to set both `content_type` and `property_set` → 400.

### Implementation for User Story 4

- [X] T034 [P] [US4] Write `ExtendedPropertySetSerializer`, `ExtendedPropertySerializer`, `ExtendedPropertyValueSerializer` (with `content_type`/`object_id` GenericFK fields) in `properties/serializers.py`
- [X] T035 [US4] Write `ExtendedPropertySetViewSet`, `ExtendedPropertyViewSet` (with `?model=<app_label>` and `?property_set=N` filters) and `ExtendedPropertyValueViewSet` (with `?model=<app_label>&object_id=N` filter) in `properties/views.py`
- [X] T036 [US4] Add `extended-properties/` and `extended-property-values/` URL registrations to `properties/urls.py`
- [X] T037 [US4] Add `?include=extended_properties` query parameter support to entity serializers: `NandSerializer`, `NandInstanceSerializer`, `NandPerfSerializer`, `CpuSerializer`, `DramSerializer` — add `extended_properties` `SerializerMethodField` that returns per-instance values filtered by `(content_type, object_id)` when param is present, otherwise `None`

### Tests for User Story 4

- [X] T038 [US4] Write ExtendedProperty tests in `tests/test_extended_props.py`: CHECK constraint rejection (both bindings set → 400, neither set → 400), per-instance value scoping (two instances return different values for same property), `UNIQUE(property, content_type, object_id)` enforcement, `?include=extended_properties` included vs omitted in entity responses

**Checkpoint**: US4 complete — extended properties and per-instance values work independently.

---

## Phase 7: User Story 5 — Configure Result Profiles, Workloads, and Record Results (Priority: P3)

**Goal**: Full CRUD for ResultProfile, ResultWorkload, ResultProfileWorkload, ResultRecord, ResultInstance with nullable hardware FKs (SET_NULL) and per-instance extended property values on ResultInstances.

**Independent Test**: Create ResultProfile + ResultWorkload → link via ResultProfileWorkload → create ResultRecord with hardware FKs → create ResultInstances → set ExtendedPropertyValues on instances → GET `/api/result-records/{id}/` returns nested instances. Delete a hardware component → ResultRecord hardware FK becomes NULL, record remains.

### Implementation for User Story 5

- [X] T039 [P] [US5] Write `ResultProfileSerializer`, `ResultWorkloadSerializer`, `ResultProfileWorkloadSerializer` (with nested `config_set` and `ext_prop_set` FK fields) in `results/serializers.py`
- [X] T040 [US5] Write `ResultRecordSerializer` (with nullable hardware FK fields) and `ResultInstanceSerializer` (with `extended_properties` SerializerMethodField) in `results/serializers.py` (same file as T039 — sequential)
- [X] T041 [US5] Write `ResultProfileViewSet`, `ResultWorkloadViewSet`, `ResultProfileWorkloadViewSet` (with `?profile=N` filter) in `results/views.py`
- [X] T042 [US5] Write `ResultRecordViewSet` (ordered by `-created_at`) and `ResultInstanceViewSet` (with `?result_record=N` filter) in `results/views.py`
- [X] T043 [US5] Write URL router in `results/urls.py` for all result endpoints: `result-profiles/`, `result-workloads/`, `result-profile-workloads/`, `result-records/`, `result-instances/`
- [X] T044 [US5] Update `config/urls.py` to include `results.urls` under `/api/` prefix

### Tests for User Story 5

- [X] T045 [US5] Write Results API tests in `tests/test_results_api.py`: `UNIQUE(profile, workload)` enforcement on ResultProfileWorkload, `UNIQUE(result_record, profile_workload)` enforcement on ResultInstance, SET_NULL behavior (delete hardware → FK becomes null, record preserved), per-instance extended property value independence across ResultInstances

**Checkpoint**: US5 complete — all user stories functional end-to-end.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, linting, final validation.

- [X] T046 [P] Update `docs/architecture.md`: data model section with all 16 new entities across 5 apps; tech stack with `django-filter` if added; bump `Last Updated`
- [X] T047 [P] Update `docs/api.md`: all new endpoint sections (hardware, properties system, results system) with request/response examples; bump `Last Updated`
- [X] T048 Update `CHANGELOG.md` under `[Unreleased]`: add model redesign feature entry (removed components/sample apps, added properties/nand/results apps, 15 new tables, 5 API namespaces)
- [X] T049 Run `ruff check .` from repo root and fix any reported issues
- [X] T050 Run quickstart.md verification: `python manage.py showmigrations` (all applied), `python manage.py shell` import all models, create a Nand via API → set ExtendedPropertyValue → retrieve with `?include=extended_properties`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately, all tasks parallel
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — models before migrations
  - T010–T013, T015–T016 can run in parallel (different files)
  - T014 depends on T013 (same file — properties/models.py)
  - T017 depends on T010–T016 (needs all models written)
  - T018 depends on T017 (needs migrations generated)
- **US2 (Phase 4)**: Depends on US1 completion (tables must exist before views can be tested)
  - T019–T022 can run in parallel (different files)
  - T022 depends on T021 (same file — nand/serializers.py)
  - T026–T027 can run in parallel (different test files)
- **US3 (Phase 5)**: Depends on US1 completion (content_type FK on models)
  - T032 depends on T019–T022 (modifies existing entity serializers)
- **US4 (Phase 6)**: Depends on US3 completion (entity serializers must support config_set before adding extended_properties param)
- **US5 (Phase 7)**: Depends on US2 + US4 completion (ResultRecord uses hardware FKs; ResultInstance uses ExtendedPropertyValue)
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

| Story | Depends On | Note |
|-------|-----------|------|
| US1 (P1) | Phase 2 only | All model code, no story deps |
| US2 (P1) | US1 | Hardware CRUD on top of schema |
| US3 (P2) | US1 | PropertyConfig uses content_type — tables must exist |
| US4 (P2) | US2 + US3 | Adds `?include=extended_properties` to entity serializers |
| US5 (P3) | US2 + US4 | ResultRecord references hardware; ResultInstance uses ExtendedPropertyValue |

### Parallel Opportunities

```
# Phase 1 — all in parallel:
T001 Remove components/  ||  T002 Remove sample/  ||  T003 Create properties/  ||  T004 Create nand/  ||  T005 Create results/

# Phase 3 model writing — in parallel (different files):
T010 cpu/models.py  ||  T011 dram/models.py  ||  T012 nand/models.py  ||  T013 properties/models.py (part 1)  ||  T015 results/models.py  ||  T016 admin files

# Phase 4 serializer writing — in parallel:
T019 cpu/serializers.py + views.py  ||  T020 dram/serializers.py + views.py  ||  T021 nand/serializers.py (Nand)

# Phase 4 tests — in parallel:
T026 test_nand_api.py  ||  T027 test_cpu_api.py + test_dram_api.py

# Phase 8 docs — in parallel:
T046 docs/architecture.md  ||  T047 docs/api.md
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (parallel)
2. Complete Phase 2: Foundational (sequential)
3. Complete Phase 3: US1 — schema/migrations
4. Complete Phase 4: US2 — hardware CRUD
5. **STOP and VALIDATE**: All hardware endpoints work, tests pass
6. Demo/deploy if ready

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 (US1) → All 15 tables exist ✓
3. Phase 4 (US2) → Hardware CRUD works ✓ (MVP!)
4. Phase 5 (US3) → Property configs work ✓
5. Phase 6 (US4) → Extended properties work ✓
6. Phase 7 (US5) → Results system works ✓
7. Phase 8 → Polished, documented ✓

---

## Notes

- [P] tasks = different files, can run in parallel without conflicts
- [Story] label maps to user story in spec.md for traceability
- `properties/models.py` has two sequential tasks (T013 → T014) — same file
- `nand/serializers.py` has two sequential tasks (T021 → T022) — same file
- `results/serializers.py` has two sequential tasks (T039 → T040) — same file
- Cross-app FK string references in `results/models.py` — use `"nand.Nand"` format (see research.md R5)
- GenericFK orphan cleanup not implemented — application responsibility per spec assumptions
- No authentication/authorization changes — follows existing project auth pattern
