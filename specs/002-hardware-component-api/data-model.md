# Data Model: Hardware Component API & Project Restructure

**Feature Branch**: `002-hardware-component-api`
**Date**: 2026-02-09

## Inheritance Strategy

Django multi-table inheritance. One base table (`components_component`) holds shared fields. Each type-specific app adds a child table linked via OneToOneField.

```
components_component (base table)
  ├── cpu_cpucomponent (child table, FK → component_ptr_id)
  └── dram_dramcomponent (child table, FK → component_ptr_id)
```

## Entities

### Component (base — `components` app)

Shared base model for all hardware components. The general `/api/components/` endpoint queries this table directly.

| Field          | Type     | Constraints                           | Description                          |
|----------------|----------|---------------------------------------|--------------------------------------|
| id             | UUID     | Primary key, auto-generated           | Unique identifier                    |
| name           | String   | Required, max 255 chars, non-blank    | Component name (e.g., "Intel i9-14900K") |
| component_type | String   | Required, max 50 chars                | Type label (e.g., "cpu", "dram")     |
| description    | Text     | Optional, blank allowed               | Detailed description                 |
| created_at     | DateTime | Auto-set on creation, indexed         | Creation timestamp                   |
| updated_at     | DateTime | Auto-set on save                      | Last modification timestamp          |

**Identity & Uniqueness**: UUID primary key. Name is not unique (multiple components can share a name).

**Validation Rules**:
- `name` is required, 1-255 characters, whitespace-only rejected
- `component_type` is required, set automatically by child models (not user-supplied on type-specific endpoints)
- `description` is optional (null or empty string)
- `id`, `created_at`, `updated_at` are system-managed, read-only via API

### CpuComponent (child — `cpu` app)

CPU-specific hardware component. Inherits all base fields from Component.

| Field       | Type    | Constraints                  | Description                               |
|-------------|---------|------------------------------|-------------------------------------------|
| cores       | Integer | Required, min 1              | Number of physical cores                  |
| threads     | Integer | Required, min 1              | Number of logical threads                 |
| clock_speed | Decimal | Required, max_digits 5, decimal_places 2 | Base clock speed in GHz     |
| boost_clock | Decimal | Optional, max_digits 5, decimal_places 2 | Max boost clock speed in GHz |
| tdp         | Integer | Optional, positive           | Thermal design power in watts             |
| socket      | String  | Optional, max 50 chars       | Socket type (e.g., "LGA1700", "AM5")      |

**Validation Rules**:
- `cores` and `threads` must be >= 1
- `threads` should be >= `cores` (validated at serializer level, not DB)
- `clock_speed` must be > 0
- `boost_clock`, if provided, must be >= `clock_speed`
- `component_type` is automatically set to `"cpu"` on save

### DramComponent (child — `dram` app)

DRAM-specific hardware component. Inherits all base fields from Component.

| Field       | Type    | Constraints                  | Description                               |
|-------------|---------|------------------------------|-------------------------------------------|
| capacity_gb | Integer | Required, positive           | Memory capacity in GB                     |
| speed_mhz   | Integer | Required, positive           | Memory speed in MHz (e.g., 3200, 6000)    |
| ddr_type    | String  | Required, max 10 chars       | DDR generation (e.g., "DDR4", "DDR5")     |
| modules     | Integer | Optional, min 1, default 1   | Number of modules in kit                  |
| cas_latency | Integer | Optional, positive           | CAS latency (CL) value                   |
| voltage     | Decimal | Optional, max_digits 3, decimal_places 2 | Operating voltage in V    |

**Validation Rules**:
- `capacity_gb` must be > 0
- `speed_mhz` must be > 0
- `ddr_type` is a free-text string (not constrained to choices, allowing for future DDR generations)
- `component_type` is automatically set to `"dram"` on save

## Relationships

```
Component (1) ←──── (0..1) CpuComponent    [multi-table inheritance: component_ptr]
Component (1) ←──── (0..1) DramComponent    [multi-table inheritance: component_ptr]
```

- Each Component record has at most ONE child record (CPU or DRAM, not both)
- The child relationship is enforced by Django's multi-table inheritance (OneToOneField named `component_ptr`)
- Deleting a Component cascades to its child record
- Deleting a child record also deletes the parent Component record

## Indexes

| Index          | Table                 | Fields         | Type    | Rationale                            |
|----------------|-----------------------|----------------|---------|--------------------------------------|
| PK             | components_component  | id             | Primary | UUID primary key                     |
| type_idx       | components_component  | component_type | B-tree  | Filter by type on general endpoint   |
| created_idx    | components_component  | created_at     | B-tree  | Ordering by creation date            |
| name_search    | components_component  | name           | GIN     | Search support (if using pg_trgm)    |
| PK             | cpu_cpucomponent      | component_ptr  | Primary | FK to Component, also PK             |
| PK             | dram_dramcomponent    | component_ptr  | Primary | FK to Component, also PK             |

## State Transitions

None. Components have no lifecycle states — they exist or they don't (simple CRUD).
