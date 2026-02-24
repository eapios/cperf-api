# Feature Specification: Backend Model Redesign

**Feature Branch**: `005-model-redesign`
**Created**: 2026-02-23
**Status**: Draft
**Input**: Redesign backend models per `docs/005-model-redesign/model-design.md`
**Design Document**: `docs/005-model-redesign/model-design.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Migrate to New Model Structure (Priority: P1)

The current multi-table inheritance hierarchy (Component -> CpuComponent, DramComponent) and the sample app are replaced by the new model structure. Since this is pre-production, a clean migration (drop old tables, create new) is acceptable.

**Why this priority**: Must happen before any new models can be used. Blocking dependency for all other stories.

**Independent Test**: Can be tested by running migrations on a fresh database and verifying all new tables exist with correct schema, and old tables are removed.

**Acceptance Scenarios**:

1. **Given** the current database with old Component/CpuComponent/DramComponent tables, **When** migrations are run, **Then** old tables are dropped and all new tables are created.
2. **Given** a fresh database, **When** migrations are run, **Then** all 15 tables are created with correct columns, constraints, and indexes.

---

### User Story 2 - CRUD Hardware Components (Priority: P1)

An engineer creates and manages NAND technologies, NAND instances, CPU components, and DRAM components through the API. Each component type has its own dedicated endpoints and field set. Data is validated at the database level (field types, constraints, unique names).

**Why this priority**: Hardware component data is the foundation — nothing else (properties, results) works without it.

**Independent Test**: Can be fully tested by creating, reading, updating, and deleting each component type via API and verifying field validation.

**Acceptance Scenarios**:

1. **Given** no NAND technologies exist, **When** the engineer creates a NAND technology with all required fields, **Then** the system stores it and returns the full record with auto-generated id and timestamps.
2. **Given** a NAND technology exists, **When** the engineer creates a NAND instance linked to it, **Then** the instance is stored with FK to the NAND technology and the unique constraint (nand + name) is enforced.
3. **Given** a NAND technology exists, **When** the engineer creates a NAND performance entry linked to it, **Then** the entry is stored with bandwidth, channel, and die_per_channel fields.
4. **Given** any component, **When** the engineer updates a field, **Then** `updated_at` is refreshed and the new value is persisted.
5. **Given** a NAND technology with instances and perf entries, **When** the engineer deletes the technology, **Then** all related instances and perf entries are cascade-deleted.
6. **Given** a ratio field (d1_d2_ratio, data_vb_die_ratio, table_vb_good_die_ratio), **When** the engineer submits a value above 1.0, **Then** the system rejects it with a validation error.

---

### User Story 3 - Manage Property Configs and Config Sets (Priority: P2)

An engineer defines rendering/display configurations (PropertyConfig) for each component type and groups them into named sets (PropertyConfigSet). The frontend optionally requests a config set to know how to render columns (display text, unit, decimal places, etc.).

**Why this priority**: Config sets control frontend rendering. Without them, the frontend can still show raw data, but cannot format columns properly.

**Independent Test**: Can be tested by creating PropertyConfigs for a component type, grouping them into a set with ordered membership, and retrieving the set via API.

**Acceptance Scenarios**:

1. **Given** a component type (e.g., Nand), **When** the engineer creates PropertyConfigs bound to that type, **Then** each config is stored with its content_type FK and the unique constraint (content_type + name) is enforced.
2. **Given** PropertyConfigs exist for Nand, **When** the engineer creates a PropertyConfigSet and adds configs via membership with indices, **Then** the set stores the ordered list and enforces unique (set + config) and unique (set + index) constraints.
3. **Given** a config set exists, **When** the frontend requests a component with `?config_set=<id>`, **Then** the response includes the config set with items ordered by index.
4. **Given** a config set exists, **When** the frontend requests a component without `?config_set`, **Then** the response omits the configs section entirely.

---

### User Story 4 - Define Extended Properties and Per-Instance Values (Priority: P2)

An engineer defines extended properties (computed or constant columns) for a component type. Each entity instance (e.g., each individual Nand) can have its own value for each extended property. Values can be formulas or literals — the backend stores them as-is; evaluation is frontend-only.

**Why this priority**: Extended properties enable user-customizable columns without schema changes, a core differentiator of this system.

**Independent Test**: Can be tested by creating an ExtendedProperty definition for a component type, setting per-instance values for two different instances, and verifying each instance returns its own values.

**Acceptance Scenarios**:

1. **Given** a component type, **When** the engineer creates an entity-level ExtendedProperty (content_type set, property_set null), **Then** it is stored and the dual-binding check constraint passes.
2. **Given** an ExtendedProperty definition exists, **When** the engineer creates ExtendedPropertyValues for two different Nand instances, **Then** each instance stores its own value and the unique constraint (property + content_type + object_id) is enforced.
3. **Given** per-instance values exist, **When** the frontend requests a component with `?include=extended_properties`, **Then** the response includes only that instance's values.
4. **Given** an ExtendedProperty, **When** the engineer attempts to set both content_type and property_set, **Then** the database rejects it via the CHECK constraint.
5. **Given** an ExtendedProperty, **When** the engineer attempts to set neither content_type nor property_set, **Then** the database rejects it via the CHECK constraint.

---

### User Story 5 - Configure Result Profiles, Workloads, and Record Results (Priority: P3)

An engineer sets up result profiles (e.g., "AIPR Upper Bound"), workloads (e.g., "GC Read"), and links them via profile-workload pairs. Each pair can have its own ExtendedPropertySet for result-level property definitions. When the frontend calculates results, it saves a ResultRecord capturing which hardware was used, and ResultInstances carrying per-instance extended property values.

**Why this priority**: Results are the output of the system. They depend on hardware components (P1) and extended properties (P2) being in place first.

**Independent Test**: Can be tested by creating profiles, workloads, linking them, creating a ResultRecord with hardware FKs, creating ResultInstances, and setting extended property values on each instance.

**Acceptance Scenarios**:

1. **Given** a profile and workload exist, **When** the engineer links them via ResultProfileWorkload, **Then** the unique constraint (profile + workload) is enforced.
2. **Given** a ResultProfileWorkload with an ExtendedPropertySet, **When** the engineer creates result-level ExtendedProperties in that set, **Then** the properties are stored with property_set FK (content_type null).
3. **Given** hardware components exist, **When** the frontend saves a ResultRecord with selected hardware, **Then** the record stores nullable FKs to nand, nand_instance, nand_perf, cpu, and dram.
4. **Given** a ResultRecord exists, **When** the system creates ResultInstances for each profile-workload pair, **Then** each instance is uniquely identified by (result_record + profile_workload).
5. **Given** ResultInstances exist, **When** the engineer sets ExtendedPropertyValues on them, **Then** each instance returns its own values independently.
6. **Given** a hardware component referenced by a ResultRecord, **When** that component is deleted, **Then** the FK is set to NULL (not cascade-deleted) and the record remains.

---

### Edge Cases

- What happens when a PropertyConfig's content_type doesn't match the PropertyConfigSet's content_type? Application-level validation rejects it; no DB constraint enforces this.
- What happens when an ExtendedPropertyValue references a deleted entity via GenericFK? GenericFK does not cascade — application must handle orphaned value cleanup.
- What happens when the same workload is added to the same profile twice? Rejected by the unique constraint on (profile, workload).
- What happens when pb_per_disk_by_channel JSON contains non-numeric values? Application-level validation on JSONField rejects it.
- What happens when a config_set query param references a set for the wrong model type? The serializer checks content_type match and returns null/omits configs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide separate CRUD endpoints for Nand, NandInstance, NandPerf, Cpu, and Dram entities.
- **FR-002**: System MUST enforce model-level validation on all model fields (types, unique constraints, FK integrity). Ratio fields (d1_d2_ratio, data_vb_die_ratio, table_vb_good_die_ratio) are constrained to ≤ 1.0 via Django's `MaxValueValidator` — this is enforced at the application layer (not a SQL CHECK constraint); raw DB inserts bypass it.
- **FR-003**: System MUST support PropertyConfig definitions bound to a model type, with unique (content_type + name) constraint.
- **FR-004**: System MUST support PropertyConfigSet as named ordered collections of PropertyConfigs, with display order stored on the through model.
- **FR-005**: System MUST support ExtendedProperty definitions with dual binding (entity-level via content_type OR result-level via property_set), enforced by a CHECK constraint.
- **FR-006**: System MUST support ExtendedPropertyValue as per-instance values linked via GenericFK, with unique (property + content_type + object_id) constraint and a composite index on (content_type, object_id).
- **FR-007**: System MUST optionally include config sets in entity responses when `?config_set=<id>` query parameter is provided.
- **FR-008**: System MUST optionally include per-instance extended property values when `?include=extended_properties` query parameter is provided.
- **FR-009**: System MUST nest Nand fields into logical groups (physical, endurance, raid, mapping, firmware, journal) in API responses while storing them flat in the database.
- **FR-010**: System MUST support ResultProfile, ResultWorkload, and ResultProfileWorkload with per-appearance ExtendedPropertySet and PropertyConfigSet FKs.
- **FR-011**: System MUST support ResultRecord with nullable hardware FKs (nand, nand_instance, nand_perf, cpu, dram) using SET_NULL on delete.
- **FR-012**: System MUST support ResultInstance identified by (result_record + profile_workload) pair with no name field.
- **FR-013**: System MUST perform a clean migration dropping old Component/CpuComponent/DramComponent tables and creating all new tables.
- **FR-014**: System MUST auto-populate created_at and updated_at timestamps on all entities.

### Key Entities

- **Nand**: NAND flash technology definition (~45 fields grouped logically). Parent of NandInstance and NandPerf.
- **NandInstance**: A specific capacity/OP configuration on a Nand technology. Belongs to one Nand.
- **NandPerf**: Performance data for a Nand technology at a specific channel config. Belongs to one Nand.
- **Cpu**: CPU component with bandwidth.
- **Dram**: DRAM component with bandwidth, channel, and transfer rate.
- **PropertyConfig**: Rendering/display config for a property column. Bound to a model type.
- **PropertyConfigSet**: Named ordered collection of PropertyConfigs for a model type.
- **PropertyConfigSetMembership**: Ordered link between a config set and a config (stores display index).
- **ExtendedPropertySet**: Named collection of ExtendedProperty definitions for result-level grouping.
- **ExtendedProperty**: Definition of a user-defined property (name + formula flag). Dual binding: model type or property set.
- **ExtendedPropertyValue**: Per-instance value for an ExtendedProperty. Linked to any entity or ResultInstance.
- **ResultProfile**: Named result grouping (e.g., "AIPR Upper Bound").
- **ResultWorkload**: Workload definition (e.g., "GC Read") with type identifier.
- **ResultProfileWorkload**: Link between profile and workload, carrying config set and property set references.
- **ResultRecord**: Saved result run with nullable hardware references. Has a name and timestamps.
- **ResultInstance**: One result entry per (result record + profile-workload pair). No name. Carries per-instance extended property values.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 16 database tables are created with correct schemas, constraints, and indexes after migration.
- **SC-002**: CRUD operations on all entity types complete successfully with proper validation (field types, unique constraints, FK integrity).
- **SC-003**: Extended property values are correctly scoped per-instance — two different entities return different values for the same property definition.
- **SC-004**: The CHECK constraint on ExtendedProperty correctly rejects rows where both or neither binding fields are set.
- **SC-005**: Entity API responses include config sets only when requested and extended properties only when requested, keeping default payloads minimal.
- **SC-006**: ResultRecord preserves hardware references on component deletion (SET_NULL) and correctly groups ResultInstances per run.
- **SC-007**: Nand API responses nest flat fields into 6 logical groups without requiring JOINs at the database level.
- **SC-008**: Old Component/CpuComponent/DramComponent tables are fully removed after migration.

## Assumptions

- This is a pre-production system — clean migration (drop + create) is acceptable; no data migration needed.
- Formula evaluation is purely frontend — backend stores formula strings as-is.
- Integer auto-increment PKs are used throughout (not UUIDs).
- GenericFK orphan cleanup (ExtendedPropertyValues pointing to deleted entities) will be handled at application level, not by DB cascades.
- PropertyConfig content_type matching within a PropertyConfigSet is enforced at application level, not by DB constraints.
- The pb_per_disk_by_channel JSONField currently only uses channels 2 and 4 but is kept flexible for future channel counts.
- Authentication/authorization is not in scope for this feature — endpoints follow the existing project auth pattern.

## Dependencies

- Existing Django project structure with `config/` package
- Django ContentTypes framework (built-in)
- Django REST Framework (already installed)
- Design document: `docs/005-model-redesign/model-design.md`
