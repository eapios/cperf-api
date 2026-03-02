# Data Model: Model Schema Fixes

**Branch**: `007-fix-model-schema` | **Date**: 2026-03-02

---

## Removed Entities

### ResultInstance (REMOVED)

Previously: junction between `ResultRecord` and `ResultProfileWorkload` with timestamps.
Deleted entirely — model, table, and all references.

---

## Modified Entities

### ResultRecord (modified)

**App**: `results`
**Base**: `properties.base.BaseEntity` (provides `name`, `created_at`, `updated_at`)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | AutoField PK | — | inherited |
| name | CharField(255) | unique | inherited from BaseEntity |
| created_at | DateTimeField | auto_now_add | inherited |
| updated_at | DateTimeField | auto_now | inherited |
| data | JSONField | null=True, blank=True, default=None | **NEW** — replaces all FK columns |

**Removed fields**: `nand`, `nand_instance`, `nand_perf`, `cpu`, `dram` (all FK → SET_NULL).

**Meta**: `ordering = ["-created_at"]`

---

### ExtendedProperty (modified)

**App**: `properties`

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | AutoField PK | — | |
| content_type | FK → ContentType | non-nullable, CASCADE | **CHANGED**: was nullable; now always required |
| name | CharField(255) | unique with content_type | |
| is_formula | BooleanField | default=False | |
| default_value | JSONField | null=True, blank=True, default=None | |

**Removed fields**: `property_set` FK → `ExtendedPropertySet`.

**Removed constraints**:
- `extended_prop_single_binding` (CHECK — exactly one of content_type/property_set)
- `unique_extended_prop_per_set` (conditional unique on property_set + name)

**Remaining constraints**:
- `unique_extended_prop_per_model_type` — simplified to unconditional `UNIQUE(content_type, name)`

---

### ExtendedPropertySet (modified — serializer only)

**App**: `properties`
No field changes. Serializer now exposes nested `items` (memberships).

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | AutoField PK | — | |
| name | CharField(255) | — | |
| content_type | FK → ContentType | null=True, blank=True | optional — scopes set to a model type |

---

## New Entities

### ExtendedPropertySetMembership (NEW)

**App**: `properties`
Junction table: `ExtendedPropertySet` ↔ `ExtendedProperty` with ordering.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | AutoField PK | — | |
| property_set | FK → ExtendedPropertySet | CASCADE, related_name="memberships" | |
| extended_property | FK → ExtendedProperty | CASCADE, related_name="memberships" | |
| index | PositiveIntegerField | — | display order within set |

**Meta**:
- `ordering = ["index"]`
- `UNIQUE(property_set, extended_property)` — name: `unique_extended_prop_in_set`
- `UNIQUE(property_set, index)` — name: `unique_index_in_extended_set`

**`__str__`**: `"{set.name}[{index}] = {property.name}"`

---

## Relationship Diagram

```
ExtendedPropertySet ──< ExtendedPropertySetMembership >── ExtendedProperty
       │                                                         │
   (content_type)                                          (content_type)
       │                                                         │
   ContentType                                             ContentType
```

```
ResultRecord
  name
  data (JSONField)        ← no FK to hardware models
```

---

## Migration Plan

### results/migrations/0002_simplify_result_record.py

1. `DeleteModel("ResultInstance")`
2. `RemoveField("ResultRecord", "nand")`
3. `RemoveField("ResultRecord", "nand_instance")`
4. `RemoveField("ResultRecord", "nand_perf")`
5. `RemoveField("ResultRecord", "cpu")`
6. `RemoveField("ResultRecord", "dram")`
7. `AddField("ResultRecord", "data", JSONField(null=True, blank=True, default=None))`

### properties/migrations/0003_extended_property_set_membership.py

1. `CreateModel("ExtendedPropertySetMembership")` with all fields and constraints
2. `RunPython` — data migration: for each `ExtendedProperty` with `property_set != null`, create `ExtendedPropertySetMembership(property_set=ep.property_set, extended_property=ep, index=0)`
3. `RunPython` — cleanup: delete `ExtendedProperty` rows where `content_type IS NULL`
4. `RemoveConstraint("ExtendedProperty", "extended_prop_single_binding")`
5. `RemoveConstraint("ExtendedProperty", "unique_extended_prop_per_set")`
6. `RemoveConstraint("ExtendedProperty", "unique_extended_prop_per_model_type")`
7. `RemoveField("ExtendedProperty", "property_set")`
8. `AlterField("ExtendedProperty", "content_type")` — remove null=True, blank=True
9. `AddConstraint("ExtendedProperty", UniqueConstraint(fields=["content_type","name"], name="unique_extended_prop_per_model_type"))`
