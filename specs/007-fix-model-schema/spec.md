# Feature Specification: Model Schema Fixes

**Feature Branch**: `007-fix-model-schema`
**Created**: 2026-02-26
**Status**: Draft
**Input**: User description: "few fixes on model: 1. simplify resultrecord: remove model resultinstance and all ids column in resultrecord, we will store a record in json column instead, 2. correction on extendedproperty: one extprop can be included in multiple set, so giving set_id to each row is not correct, maybe a membership table like what we do for propertyconfig will do, 3. additional hint for you: we should almost only use extendedproperty for property that are not likely to change to avoid too many extendedpropertyvalue rows, such as formula and fixed value, when user want to add a property that different for every target, they should tell backend dev to add a property for the model instead"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store Result Record as a JSON Blob (Priority: P1)

A backend consumer creates a result record by posting a JSON payload that captures all relevant hardware and configuration details at the time of recording. The system stores this blob without enforcing referential integrity to individual hardware rows.

**Why this priority**: Removes the largest structural change (dropping ResultInstance and all FK columns from ResultRecord), eliminating join complexity and making result records self-contained.

**Independent Test**: A POST request to `/api/result-records/` with a `data` JSON field succeeds and the value is retrievable via GET without any FK fields present.

**Acceptance Scenarios**:

1. **Given** a client wants to record a test result, **When** they POST `{ "name": "run-001", "data": { "nand": { ... }, "cpu": { ... } } }`, **Then** a ResultRecord is created with the JSON blob stored verbatim.
2. **Given** an existing ResultRecord, **When** a client performs GET, **Then** the response contains the `data` JSON field and no `nand`, `nand_instance`, `nand_perf`, `cpu`, or `dram` FK fields.
3. **Given** the results app, **When** a developer inspects the schema, **Then** the `ResultInstance` table no longer exists and `ResultRecord` has no FK columns to hardware tables.

---

### User Story 2 - Assign One ExtendedProperty to Multiple Sets (Priority: P2)

A developer who configures property sets can add the same `ExtendedProperty` to more than one `ExtendedPropertySet` without duplicating the property definition.

**Why this priority**: Fixes a structural data-model bug where a single FK on `ExtendedProperty` prevents reuse across sets.

**Independent Test**: Two distinct ExtendedPropertySets can reference the same ExtendedProperty via the membership table, and querying either set returns that property.

**Acceptance Scenarios**:

1. **Given** an ExtendedProperty `ep-1`, **When** a developer adds it to both `Set A` and `Set B` via the membership endpoint, **Then** both sets list `ep-1` when queried.
2. **Given** the schema, **When** a developer inspects `ExtendedProperty`, **Then** no `property_set` FK column exists on the table.
3. **Given** the schema, **When** a developer inspects the new membership table, **Then** it has `property_set`, `extended_property`, and `index` columns with the same uniqueness constraints as `PropertyConfigSetMembership`.

---

### User Story 3 - Enforce ExtendedProperty Usage Guidance (Priority: P3)

A developer adding a new property to the system follows documented guidance to decide between adding an `ExtendedProperty` (for static/formula/fixed values) versus adding a native model field (for per-instance variable values).

**Why this priority**: Design-level constraint that prevents future data-model bloat from misuse of `ExtendedPropertyValue`.

**Independent Test**: The architecture documentation describes when to use ExtendedProperty vs a native model field, with a clear rule and an example for each case.

**Acceptance Scenarios**:

1. **Given** a property whose value is the same formula for all instances, **When** a developer adds it, **Then** they use `ExtendedProperty` with `is_formula=True` and a `default_value`.
2. **Given** a property that is different for every hardware instance (e.g., a per-device calibration value), **When** a developer needs to add it, **Then** they add a native model field to the relevant Django model rather than creating an `ExtendedProperty`.
3. **Given** the architecture documentation, **When** a developer reads it, **Then** it clearly states: ExtendedProperty is for values unlikely to change across instances; variable per-instance data must be native model fields.

---

### Edge Cases

- What happens to existing `ExtendedPropertyValue` rows when their `ExtendedProperty` loses its `property_set` FK during migration? Membership table must be pre-populated before the FK column is dropped.
- What happens if a client POSTs a ResultRecord with legacy FK field names (e.g., `nand`)? Those fields no longer exist in the model and will be ignored or raise a validation error.
- What happens if a ResultRecord's `data` field is `null` or missing? The field accepts `null` to allow empty records.
- What happens to previously existing `ResultInstance` rows during migration? They must be dropped before the table is removed.

---

## Requirements *(mandatory)*

### Functional Requirements

**ResultRecord simplification:**

- **FR-001**: The `ResultRecord` model MUST replace all FK columns (`nand`, `nand_instance`, `nand_perf`, `cpu`, `dram`) with a single `data` JSON column (nullable, blank allowed).
- **FR-002**: The `ResultInstance` model and its associated database table MUST be removed entirely.
- **FR-003**: The `/api/result-instances/` endpoint MUST be removed.
- **FR-004**: Existing `ResultRecord` API endpoints (`GET`, `POST`, `DELETE` on `/api/result-records/`) MUST continue to function with the new schema.

**ExtendedProperty set membership:**

- **FR-005**: A new `ExtendedPropertySetMembership` junction table MUST be introduced with FK columns to `ExtendedPropertySet` and `ExtendedProperty`, an `index` ordering field, and uniqueness constraints on `(property_set, extended_property)` and `(property_set, index)`.
- **FR-006**: The `property_set` FK column on `ExtendedProperty` MUST be removed.
- **FR-007**: The CHECK constraint "exactly one of (content_type, property_set) is non-null" on `ExtendedProperty` MUST be removed; `content_type` becomes a required non-nullable FK.
- **FR-008**: CRUD endpoints for `ExtendedPropertySetMembership` MUST be available, following the same conventions as `PropertyConfigSetMembership`.

**ExtendedProperty usage policy:**

- **FR-009**: Architecture and API documentation MUST state that `ExtendedProperty` is reserved for values that are static or formula-based across most instances (e.g., formula, fixed value, default constant).
- **FR-010**: Documentation MUST state that when a property is expected to differ for every instance, a native model field MUST be added to the relevant Django model instead.

### Key Entities

- **ResultRecord**: A named entity capturing a complete test result. The `data` JSON column stores a free-form snapshot of all relevant hardware and configuration at record time. No longer references hardware rows directly.
- **ExtendedProperty**: A named, type-tagged property definition, always bound to a specific content type (required, non-nullable). Belongs to zero or more `ExtendedPropertySet` instances via `ExtendedPropertySetMembership`. Appropriate only for static or formula-based values.
- **ExtendedPropertySet**: A named, optionally content-type-scoped group of `ExtendedProperty` definitions.
- **ExtendedPropertySetMembership**: Junction table linking one `ExtendedProperty` to one `ExtendedPropertySet` with an ordering index. Mirrors the structure of `PropertyConfigSetMembership`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All existing tests pass after schema migrations are applied with zero failures.
- **SC-002**: A ResultRecord can be created, retrieved, and deleted with only a `name` and `data` field — no hardware FK fields are present or required.
- **SC-003**: A single ExtendedProperty can be assigned to two or more ExtendedPropertySets, verified by querying both sets and confirming the property appears in each.
- **SC-004**: Architecture documentation is updated to reflect the removed models, the new membership table, and the ExtendedProperty usage policy.
- **SC-005**: Zero `ResultInstance`-related endpoints or model references remain in the codebase after the change.

---

## Assumptions

- Existing `ResultRecord` rows with data stored in FK columns are not being migrated to the JSON format; a clean migration (dropping columns) is acceptable without data preservation.
- `ExtendedPropertyValue` rows referencing properties previously set-bound via `property_set` FK are not affected functionally — the membership table addition does not alter how values are resolved.
- The `ExtendedProperty.content_type` field, previously nullable, becomes required (non-nullable). Any existing rows with `content_type IS NULL` must be resolved before the migration runs.
- The `ExtendedPropertySetMembership` API follows the same design conventions as `PropertyConfigSetMembership` (list, create, delete; no update).

## Implementation Decisions

- **`ResultRecord.data` default**: `null` (not `{}`). The field is nullable and blank-allowed; null signals an empty/unset record without imposing a default shape.
- **`ExtendedProperty` filter**: Replace the now-removed `property_set` NumberFilter with a `?set=<set_id>` filter that queries through `ExtendedPropertySetMembership`. Remove the old `property_set` filter.
- **`ExtendedPropertySet` serializer**: Include a nested `items` field (inline memberships) following the same pattern as `PropertyConfigSet`. The membership serializer mirrors `PropertyConfigSetMembershipSerializer`.
- **Test strategy**:
  - `TestResultInstance` — delete entirely (covers the removed `ResultInstance` model).
  - `TestResultLevelPropertyResolve` — rewrite using `content_type` binding (e.g. `ResultWorkload` content type) instead of `property_set`.
  - `TestExtendedPropertyBinding` — rewrite: drop "both bindings" and "neither binding" cases; replace with "content_type required, property_set no longer exists".

