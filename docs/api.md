# API Reference

Last Updated: 2026-03-02

## Base URL

```
http://localhost:8000
```

**Authentication**: None (all endpoints use `AllowAny`).

## Common Behaviour

All list endpoints support: search (`?search=`), ordering (`?ordering=`), pagination (`?page=`, 20 per page).

All list endpoints return a paginated envelope:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/nand/?page=2",
  "previous": null,
  "results": [...]
}
```

Validation errors return **400** with field-level messages.

## Endpoint Index

### Hardware

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/nand/` | GET, POST, PUT, PATCH, DELETE | NAND technology definitions |
| `/api/nand-instances/` | GET, POST, PUT, PATCH, DELETE | NAND capacity/OP instances |
| `/api/nand-perf/` | GET, POST, PUT, PATCH, DELETE | NAND performance entries |
| `/api/cpu/` | GET, POST, PUT, PATCH, DELETE | CPU definitions |
| `/api/dram/` | GET, POST, PUT, PATCH, DELETE | DRAM definitions |

### Properties System

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/property-configs/` | GET, POST, PUT, PATCH, DELETE | Column/field configuration definitions |
| `/api/config-sets/` | GET, POST, PUT, PATCH, DELETE | Ordered sets of property configs |
| `/api/extended-property-sets/` | GET, POST, PUT, PATCH, DELETE | Named sets of extended properties |
| `/api/extended-property-set-memberships/` | GET, POST, DELETE | Links a property to a set with an ordering index |
| `/api/extended-properties/` | GET, POST, PUT, PATCH, DELETE | Extended property definitions |
| `/api/extended-property-values/` | GET, POST, PUT, PATCH, DELETE | Per-instance extended property values |

### Results System

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/result-profiles/` | GET, POST, PUT, PATCH, DELETE | Result profiles (groupings) |
| `/api/result-workloads/` | GET, POST, PUT, PATCH, DELETE | Workload definitions |
| `/api/result-profile-workloads/` | GET, POST, PUT, PATCH, DELETE | Profile ↔ workload links |
| `/api/result-records/` | GET, POST, DELETE | Result runs (no PUT/PATCH) |

---

## Hardware Endpoints

### Optional Query Parameters (all hardware detail endpoints)

- `?config_set=<id>` — includes the named PropertyConfigSet in the response under the `config_set` key; the key is `null` when the param is absent.
- `?include=extended_properties` — includes all per-instance ExtendedPropertyValues in the response under `extended_properties`; the key is `null` when the param is absent.

---

### Nand

Stores flat but **reads nested**. GET responses group fields into logical sections; POST/PUT/PATCH accept flat field names.

**Fields (write — flat)**

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | max 255 |
| capacity_per_die | positive integer | bytes |
| plane_per_die | positive small integer | |
| block_per_plane | positive integer | |
| d1_d2_ratio | float | ≤ 1.0 |
| page_per_block | positive integer | |
| slc_page_per_block | positive integer | |
| node_per_page | positive integer | |
| finger_per_wl | positive small integer | |
| tlc_qlc_pe | positive integer | P/E cycles |
| static_slc_pe | positive integer | |
| table_slc_pe | positive integer | |
| bad_block_ratio | float | |
| max_data_raid_frame | positive integer | |
| max_slc_wc_raid_frame | positive integer | |
| max_table_raid_frame | positive integer | |
| data_die_raid | positive integer | |
| table_die_raid | positive integer | |
| l2p_unit | positive integer | |
| mapping_table_size | positive big integer | |
| p2l_entry | positive integer | |
| with_p2l | positive small integer | |
| p2l_bitmap | positive integer | |
| l2p_ecc_data | positive integer | |
| l2p_ecc_spare | positive integer | |
| reserved_lca_number | positive integer | |
| day_per_year | positive small integer | default 365 |
| power_cycle_count | positive integer | |
| default_rebuild_time | positive integer | |
| drive_log_region_size | positive integer | |
| drive_log_min_op | float | |
| using_slc_write_cache | boolean | |
| using_pmd | boolean | |
| min_mapping_op_with_pmd | float | |
| data_open | positive small integer | |
| data_open_with_slc_wc | positive small integer | |
| data_gc_damper_central | float | |
| min_pfail_vb | positive integer | |
| small_table_vb | positive integer | |
| pfail_max_plane_count | positive small integer | |
| bol_block_number | positive integer | |
| extra_table_life_for_align_spec | float | |
| pb_per_disk_by_channel | JSON object | `{"2": 100, "4": 200}` |
| journal_insert_time | positive integer | |
| journal_entry_size | positive integer | |
| journal_program_unit | positive integer | |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

**GET response structure**

```json
{
  "id": 1,
  "name": "BiCS8",
  "physical": {
    "capacity_per_die": 1099511627776,
    "plane_per_die": 4,
    "block_per_plane": 2048,
    "d1_d2_ratio": 0.5,
    "page_per_block": 256,
    "slc_page_per_block": 64,
    "node_per_page": 16,
    "finger_per_wl": 2
  },
  "endurance": { "tlc_qlc_pe": 3000, "static_slc_pe": 100000, "table_slc_pe": 60000, "bad_block_ratio": 0.02 },
  "raid": { "max_data_raid_frame": 4, "max_slc_wc_raid_frame": 2, "max_table_raid_frame": 2, "data_die_raid": 16, "table_die_raid": 4 },
  "mapping": { "l2p_unit": 4096, "mapping_table_size": 536870912, "p2l_entry": 512, "with_p2l": 1, "p2l_bitmap": 256, "l2p_ecc_data": 8, "l2p_ecc_spare": 2, "reserved_lca_number": 256 },
  "firmware": { "day_per_year": 365, "power_cycle_count": 1000, "...": "..." },
  "journal": { "journal_insert_time": 1000, "journal_entry_size": 64, "journal_program_unit": 4 },
  "pb_per_disk_by_channel": {"2": 100},
  "config_set": null,
  "extended_properties": null,
  "created_at": "2026-02-24T00:00:00Z",
  "updated_at": "2026-02-24T00:00:00Z"
}
```

---

### NandInstance

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | max 255; UNIQUE per nand |
| nand | integer (FK) | |
| module_capacity | positive big integer | |
| user_capacity | positive big integer | |
| namespace_num | positive small integer | |
| ns_remap_table_unit | positive integer | |
| data_pca_width | positive small integer | |
| l2p_width | positive small integer | |
| data_vb_die_ratio | float | ≤ 1.0 |
| page_num_per_raid_tag | positive integer | |
| p2l_node_per_data_p2l_group | positive integer | |
| data_p2l_group_num | positive integer | |
| table_vb_good_die_ratio | float | ≤ 1.0 |
| config_set | object \| null | via `?config_set=<id>` |
| extended_properties | array \| null | via `?include=extended_properties` |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

**Filter**: `?nand=<id>`

---

### NandPerf

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| nand | integer (FK) | |
| bandwidth | float | |
| module_capacity | positive big integer | |
| channel | positive small integer | |
| die_per_channel | positive small integer | |
| config_set | object \| null | via `?config_set=<id>` |
| extended_properties | array \| null | via `?include=extended_properties` |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

**Filter**: `?nand=<id>`

---

### Cpu

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| bandwidth | float | |
| config_set | object \| null | via `?config_set=<id>` |
| extended_properties | array \| null | via `?include=extended_properties` |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

---

### Dram

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| bandwidth | float | |
| channel | positive small integer | |
| transfer_rate | float | |
| config_set | object \| null | via `?config_set=<id>` |
| extended_properties | array \| null | via `?include=extended_properties` |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

---

## Properties System Endpoints

### PropertyConfig

Defines a configurable column/field for a given content type.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| content_type | integer (FK) | Django ContentType pk |
| name | string | UNIQUE per content_type |
| display_text | string | |
| description | string | |
| read_only | boolean | |
| is_extended | boolean | |
| is_primary | boolean | |
| is_numeric | boolean | |
| sub_type | string | |
| decimal_place | integer | |
| unit | string | |

**Filter**: `?model=<app_label>` (e.g. `?model=nand`)

---

### PropertyConfigSet

An ordered set of PropertyConfigs for a content type.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| content_type | integer (FK) | UNIQUE per name |
| name | string | |
| items | array | nested memberships ordered by `index` |

Each item in `items`:

```json
{ "id": 1, "index": 0, "config": { "id": 5, "name": "capacity_per_die", "display_text": "Capacity/Die", "unit": "B", "decimal_place": 0, "is_numeric": true } }
```

---

### ExtendedPropertySet

A named group of extended properties, optionally scoped to a content type. Members are linked via `ExtendedPropertySetMembership`.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| content_type | integer \| null | optional scoping |
| items | array | nested memberships ordered by `index` |

Each item in `items`:

```json
{ "id": 1, "index": 0, "extended_property": { "id": 3, "content_type": 7, "name": "Latency", "is_formula": true, "default_value": "=A/B" } }
```

---

### ExtendedPropertySetMembership

Links one `ExtendedProperty` to one `ExtendedPropertySet` with an ordering index. The same property may belong to multiple sets. **No PUT/PATCH** — delete and recreate to reorder.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| property_set_id | integer (write) | set to add the property to |
| extended_property_id | integer (write) | property to add |
| index | integer | display order within the set |
| extended_property | object (read) | nested ExtendedProperty definition |

UNIQUE constraints: `(property_set, extended_property)`, `(property_set, index)`.

---

### ExtendedProperty

A single extended property definition. `content_type` is **always required**. A property belongs to zero or more `ExtendedPropertySet`s via `ExtendedPropertySetMembership`.

**Usage policy**: Use only for values that are static or formula-based across most instances (e.g. formulas, fixed constants). For values that differ per hardware instance, add a native model field instead.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| content_type | integer (FK) | required — model type this property is bound to |
| name | string | UNIQUE per content_type |
| is_formula | boolean | |
| default_value | any JSON \| null | fallback for instances with no per-instance value record; null means no default defined |

**Filters**: `?model=<app_label>`, `?set=<set_id>`

#### `GET /api/extended-properties/{id}/resolve/`

Returns the effective value for a given instance: the per-instance `ExtendedPropertyValue` if one exists, otherwise `default_value`.

**Query parameters** (all required except `model_name`):

| Parameter | Type | Notes |
|-----------|------|-------|
| model | string | App label of the target model (e.g. `cpu`, `nand`, `results`) |
| model_name | string | Model class name — required when the app has multiple models (e.g. `resultworkload`) |
| object_id | integer | PK of the target instance |

**Response 200**:
```json
{ "property_id": 5, "value": 65, "is_default": true }
```
`is_default: true` — value comes from `default_value` (no per-instance record).
`is_default: false` — value comes from a per-instance `ExtendedPropertyValue` record.

**Errors**: `400` missing params or ambiguous `model`; `404` unknown property or model.

---

### ExtendedPropertyValue

A per-instance value for an ExtendedProperty, identified by a GenericForeignKey (`content_type` + `object_id`).

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| extended_property | integer (FK) | |
| content_type | integer (FK) | entity type |
| object_id | integer | entity PK |
| value | string | formula string or literal |

UNIQUE constraint: `(extended_property, content_type, object_id)` — one value per property per instance.

**Filters**: `?model=<app_label>`, `?object_id=<id>`

---

## Results System Endpoints

### ResultProfile

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | unique |

---

### ResultWorkload

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| type | integer | opaque workload type identifier |

---

### ResultProfileWorkload

Links a workload to a profile. UNIQUE per `(profile, workload)`.

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| profile | integer (FK) | |
| workload | integer (FK) | |
| config_set | integer \| null | optional PropertyConfigSet |
| extended_property_set | integer \| null | optional ExtendedPropertySet |

**Filter**: `?profile=<id>`

---

### ResultRecord

A result run. Stores a free-form JSON snapshot of hardware and configuration at record time; no FK references to hardware rows. Ordered by `-created_at`. **No PUT/PATCH** (immutable after creation).

| Field | Type | Notes |
|-------|------|-------|
| id | integer | read-only |
| name | string | |
| data | any JSON \| null | free-form snapshot of hardware/config; null = empty record |
| created_at | datetime | read-only |
| updated_at | datetime | read-only |

**Example request**:

```json
{ "name": "run-001", "data": { "nand": { "name": "BiCS8", "capacity_per_die": 1099511627776 }, "cpu": { "name": "A100" } } }
```
