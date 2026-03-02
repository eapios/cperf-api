# Research: Model Schema Fixes

**Branch**: `007-fix-model-schema` | **Date**: 2026-03-02

All decisions resolved from spec, existing codebase patterns, and prior clarification. No external research required.

---

## Decision Log

### D-001: JSONField for ResultRecord.data

- **Decision**: `models.JSONField(null=True, blank=True, default=None)`
- **Rationale**: Django's built-in JSONField is available since Django 3.1; no extra dependency needed. `null=True` matches the spec requirement that empty records are valid. `default=None` avoids mutable default pitfalls.
- **Alternatives considered**: `default=dict` — rejected (hides missing data, imposes shape).

### D-002: Migration order for ResultRecord

- **Decision**: Single migration `results/0002` — delete ResultInstance rows, drop ResultInstance table, remove FK columns, add `data` JSONField.
- **Rationale**: Atomic; SQLite (dev) and PostgreSQL (Docker) both support column drops via Django migrations.
- **Alternatives considered**: Two separate migrations — unnecessary complexity.

### D-003: ExtendedPropertySetMembership mirrors PropertyConfigSetMembership exactly

- **Decision**: Same field names (`property_set`, `extended_property`, `index`), same constraints (`unique_extended_prop_in_set`, `unique_index_in_extended_set`), same API shape (list/create/delete, no update).
- **Rationale**: Consistent codebase pattern already validated in production. Minimises cognitive overhead.
- **Alternatives considered**: Generic through-model — rejected (YAGNI).

### D-004: Properties migration strategy (0003)

- **Decision**: Three-step migration:
  1. Create `ExtendedPropertySetMembership` table.
  2. Data-migrate existing `ExtendedProperty` rows where `property_set IS NOT NULL` → insert membership rows with `index=0`.
  3. Delete any `ExtendedProperty` rows where `content_type IS NULL` (invalid after this change).
  4. Drop `property_set` FK column; make `content_type` non-nullable.
  5. Remove old constraints (`unique_extended_prop_per_set`, `extended_prop_single_binding`); simplify remaining unique constraint to unconditional `(content_type, name)`.
- **Rationale**: Spec assumption explicitly states dev environment — no data preservation required for null content_type rows.
- **Alternatives considered**: Requiring manual data cleanup before migration — rejected (bad DX).

### D-005: ExtendedProperty filter replacement

- **Decision**: Remove `property_set` NumberFilter; add `set` NumberFilter querying `memberships__property_set_id`.
- **Rationale**: Direct replacement; preserves filter ergonomics for callers.

### D-006: ExtendedPropertySet serializer with nested items

- **Decision**: Add `items = ExtendedPropertySetMembershipSerializer(source="memberships", many=True, read_only=True)` — same pattern as `PropertyConfigSetSerializer`.
- **Rationale**: Consistent with existing pattern; single GET returns a usable set with its members.

### D-007: ExtendedPropertySet queryset prefetch

- **Decision**: `ExtendedPropertySetViewSet.queryset` gains `.prefetch_related("memberships__extended_property")`.
- **Rationale**: Prevents N+1 when rendering nested items.
