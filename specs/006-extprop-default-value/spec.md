# Feature Specification: Extended Property Default Value

**Feature Branch**: `006-extprop-default-value`
**Created**: 2026-02-24
**Status**: Draft
**Input**: User description: "i want to add a default_value in the model ExtendedProperty, so it can work without the value table"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define a Default Value for a Property (Priority: P1)

A data administrator defines an extended property (e.g., "Thermal Design Power") and sets a default value of `0`. All hardware instances that do not have a specific value recorded for this property automatically display `0` without requiring individual value records to be created for each instance.

**Why this priority**: This is the core value of the feature — it eliminates the need to populate the value table for every instance when a common default applies.

**Independent Test**: Can be fully tested by creating an `ExtendedProperty` with a `default_value`, then querying any instance that has no associated value record and verifying the default is returned.

**Acceptance Scenarios**:

1. **Given** an `ExtendedProperty` with `default_value = 65`, **When** a client requests the property value for an instance that has no per-instance value record, **Then** the response contains `65` as the value.
2. **Given** an `ExtendedProperty` with `default_value = null`, **When** a client requests the property value for an instance that has no per-instance value record, **Then** the response indicates no value is available for that property.
3. **Given** an `ExtendedProperty` with `default_value = "TBD"`, **When** a new instance is added to the system without any value record for that property, **Then** querying the instance returns `"TBD"` without any extra configuration.

---

### User Story 2 - Per-Instance Value Takes Precedence (Priority: P2)

A per-instance value record overrides the default value. A data administrator sets `default_value = 0` on a property, but one specific instance has a recorded value of `125`. Querying that instance returns `125`, not `0`.

**Why this priority**: The override precedence is essential for correctness — without it, the default could silently shadow real data.

**Independent Test**: Can be tested by creating an `ExtendedProperty` with a `default_value`, adding one `ExtendedPropertyValue` record for a specific instance, and verifying the per-instance value is returned for that instance while the default is returned for all others.

**Acceptance Scenarios**:

1. **Given** an `ExtendedProperty` with `default_value = 0` and an `ExtendedPropertyValue` of `125` for instance A, **When** querying instance A, **Then** `125` is returned (not `0`).
2. **Given** the same setup, **When** querying instance B (no value record), **Then** `0` (the default) is returned.

---

### User Story 3 - Formula Properties Support Default Value (Priority: P3)

A formula-based extended property (`is_formula = true`) can define a default formula expression as its `default_value`. Instances without a per-instance formula record use the default formula.

**Why this priority**: Formula properties follow the same value-lookup pattern; supporting defaults here completes the feature uniformly.

**Independent Test**: Can be tested by creating a formula `ExtendedProperty` with a `default_value` containing a formula string, then querying an instance with no value record and verifying the default formula string is returned.

**Acceptance Scenarios**:

1. **Given** a formula `ExtendedProperty` with `default_value = "A / B"`, **When** querying an instance with no per-instance formula record, **Then** the formula string `"A / B"` is returned as the default.

---

### Edge Cases

- What happens when `default_value` is set to an empty string vs. null? Null means "no default defined"; empty string is a valid literal default value.
- What happens when `default_value` changes after instances already have per-instance value records? Per-instance values are unaffected; instances without records immediately reflect the updated default.
- What happens when the property's `is_formula` flag is true but `default_value` contains a non-formula literal? The value is stored and returned as-is — interpretation is the caller's responsibility (same semantics as `ExtendedPropertyValue.value`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `ExtendedProperty` MUST support an optional `default_value` field that accepts any data type (text, number, boolean, null, structured object).
- **FR-002**: The `default_value` field MUST default to null when not specified, meaning no default is defined for that property.
- **FR-003**: When resolving a property value for a given instance, the system MUST return the per-instance value if one exists.
- **FR-004**: When no per-instance value exists for a given instance, the system MUST return the property's `default_value` (which may itself be null).
- **FR-005**: `default_value` MUST be applicable to both entity-level and result-level properties.
- **FR-006**: The `default_value` field MUST be settable and updatable via the standard property management interface.

### Key Entities

- **ExtendedProperty**: Definition of a user-defined property. Gains an optional `default_value` attribute that applies to all instances lacking a per-instance value record.
- **ExtendedPropertyValue**: A per-instance override. Takes precedence over `ExtendedProperty.default_value` when present.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of extended properties (both entity-level and result-level) can define a `default_value` without requiring any per-instance value records to exist.
- **SC-002**: When querying a property for an instance with no value record, the response correctly reflects the `default_value` — no additional steps required by the caller.
- **SC-003**: All existing per-instance value lookups continue to return correct values with no regressions.
- **SC-004**: Creating or updating an `ExtendedProperty` with a `default_value` completes successfully and the value is immediately reflected in subsequent reads.

## Assumptions

- `default_value` uses the same data representation as `ExtendedPropertyValue.value` (any JSON-compatible type).
- Null `default_value` means "undefined" — the property has no fallback for instances without a value record.
- The feature does not add logic to evaluate formula defaults; it only stores and returns the formula string, consistent with how per-instance formula values are handled today.
- No migration of existing data is required — all existing `ExtendedProperty` records will have `default_value = null` after the migration.

