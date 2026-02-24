# Research: Backend Model Redesign

**Feature**: 005-model-redesign
**Date**: 2026-02-23

## Phase 0: Research Findings

No NEEDS CLARIFICATION items exist in the spec or technical context. All design decisions are pre-resolved in `docs/005-model-redesign/model-design.md`. This document records rationale for key technical choices.

### R1: GenericForeignKey for ExtendedPropertyValue

**Decision**: Use Django's `GenericForeignKey` (contenttypes framework) for `ExtendedPropertyValue` to point to any entity type (Nand, Cpu, Dram, NandInstance, NandPerf, ResultInstance).

**Rationale**: Only 6 target model types, low data volume. GenericFK provides a single table for all values with a unified query pattern. The composite index on (content_type, object_id) ensures fast lookups per instance.

**Alternatives considered**:
- Separate value tables per model type (NandExtendedValue, CpuExtendedValue, etc.) — rejected: 6 near-identical tables, violates DRY, complicates serializer pattern.
- JSONField on each model — rejected: no per-property uniqueness constraint, no query capability per property.

**Known limitation**: GenericFK does not cascade on delete. Orphaned `ExtendedPropertyValue` rows must be cleaned up at application level (documented in spec assumptions).

### R2: Clean Migration Strategy

**Decision**: Drop all old tables (components_component, cpu_cpucomponent, dram_dramcomponent) and create new tables from scratch.

**Rationale**: Pre-production system with no real data. Clean migration avoids complex data transformation and ensures no schema artifacts from old models remain.

**Approach**:
1. Remove `components` app entirely (delete directory)
2. Rewrite `cpu` and `dram` models in-place
3. Run `makemigrations` for all apps — Django generates drop + create operations
4. Run `migrate` to apply

### R3: Nand Field Grouping in API Response

**Decision**: Store all ~45 Nand fields in a single flat table but nest them into 6 logical groups (physical, endurance, raid, mapping, firmware, journal) in the API serializer.

**Rationale**: Flat table = no JOINs for reads/writes. Nested serializer = clean API contract for frontend. Mapping between flat and nested is purely in the serializer layer.

**Approach**: Use nested serializers in DRF — one read-only serializer per group that maps to the same model instance's fields. Write operations accept flat or nested (TBD during implementation — flat is simpler for MVP).

### R4: Optional Query Parameters for Configs and Extended Properties

**Decision**: Configs via `?config_set=<id>`, extended properties via `?include=extended_properties`.

**Rationale**: Keeps default entity responses minimal (just data fields + timestamps). Frontend requests metadata only when needed.

**Approach**: `SerializerMethodField` in DRF serializers that check `request.query_params`. Return `None` (omitted from response) when not requested.

### R5: String References for Cross-App FKs in ResultRecord

**Decision**: Use Django string references (`"nand.Nand"`) instead of direct imports for ForeignKey targets in `results/models.py`.

**Rationale**: Avoids circular import risk between results → nand/cpu/dram apps. Django resolves string references at runtime via the app registry.
