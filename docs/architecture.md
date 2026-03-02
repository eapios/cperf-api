# Architecture

Last Updated: 2026-03-02

## System Overview

Django REST API for managing NAND-based SSD performance data. Provides full CRUD operations for hardware components (Nand, NandInstance, NandPerf, Cpu, Dram), a property configuration system for customisable result views, an extended property system for static/formula-based computed values, and a results system for recording test outcomes as free-form JSON snapshots.

## Technology Stack


| Component       | Technology                 | Purpose                     |
| --------------- | -------------------------- | --------------------------- |
| Language        | Python 3.12                | Runtime                     |
| Framework       | Django 5.1                 | Web framework               |
| API             | Django REST Framework 3.15 | REST API toolkit            |
| Database (prod) | PostgreSQL 16              | Primary datastore (Docker)  |
| Database (dev)  | SQLite 3                   | Local development datastore |
| Config          | django-environ             | Environment-based settings  |
| Filtering       | django-filter              | Queryset filtering for API  |
| DB Driver       | psycopg2-binary            | PostgreSQL adapter          |
| Debugging       | debugpy                    | Remote debugger for Docker  |


## Data Model

15 database tables across 5 Django apps.

---

### Field Reference

Shared columns (`id`, `name`, `created_at`, `updated_at`) come from `BaseEntity` (abstract) unless noted.

#### BaseEntity (abstract)

No DB table — fields are copied into each child model at class definition time.

| Field | Type | Null | Default |
|-------|------|------|---------|
| id | BigAutoField | No | — |
| name | CharField(255) | No | — |
| created_at | DateTimeField | No | auto_now_add |
| updated_at | DateTimeField | No | auto_now |

Inherited by: `Cpu`, `Dram`, `Nand`, `NandInstance`, `NandPerf`, `ResultRecord`.

#### Hardware Apps

##### Cpu (`cpu` app)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | from BaseEntity |
| bandwidth | FloatField | No | — | |
| created_at | DateTimeField | No | auto | from BaseEntity |
| updated_at | DateTimeField | No | auto | from BaseEntity |

##### Dram (`dram` app)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | from BaseEntity |
| bandwidth | FloatField | No | — | |
| channel | PositiveSmallIntegerField | No | — | |
| transfer_rate | FloatField | No | — | |
| created_at | DateTimeField | No | auto | from BaseEntity |
| updated_at | DateTimeField | No | auto | from BaseEntity |

##### Nand (`nand` app — 3 tables)

**Nand**

| Field | Group | Type | Null | Default | Notes |
|-------|-------|------|------|---------|-------|
| id | — | BigAutoField | No | — | PK |
| name | — | CharField(255) | No | — | from BaseEntity |
| capacity_per_die | Physical | PositiveIntegerField | No | — | bytes |
| plane_per_die | Physical | PositiveSmallIntegerField | No | — | |
| block_per_plane | Physical | PositiveIntegerField | No | — | |
| d1_d2_ratio | Physical | FloatField | No | — | ≤ 1.0 |
| page_per_block | Physical | PositiveIntegerField | No | — | |
| slc_page_per_block | Physical | PositiveIntegerField | No | — | |
| node_per_page | Physical | PositiveIntegerField | No | — | |
| finger_per_wl | Physical | PositiveSmallIntegerField | No | — | |
| tlc_qlc_pe | Endurance | PositiveIntegerField | No | — | P/E cycles |
| static_slc_pe | Endurance | PositiveIntegerField | No | — | |
| table_slc_pe | Endurance | PositiveIntegerField | No | — | |
| bad_block_ratio | Endurance | FloatField | No | — | |
| max_data_raid_frame | RAID | PositiveIntegerField | No | — | |
| max_slc_wc_raid_frame | RAID | PositiveIntegerField | No | — | |
| max_table_raid_frame | RAID | PositiveIntegerField | No | — | |
| data_die_raid | RAID | PositiveIntegerField | No | — | |
| table_die_raid | RAID | PositiveIntegerField | No | — | |
| l2p_unit | Mapping | PositiveIntegerField | No | — | |
| mapping_table_size | Mapping | PositiveBigIntegerField | No | — | |
| p2l_entry | Mapping | PositiveIntegerField | No | — | |
| with_p2l | Mapping | PositiveSmallIntegerField | No | — | |
| p2l_bitmap | Mapping | PositiveIntegerField | No | — | |
| l2p_ecc_data | Mapping | PositiveIntegerField | No | — | |
| l2p_ecc_spare | Mapping | PositiveIntegerField | No | — | |
| reserved_lca_number | Mapping | PositiveIntegerField | No | — | |
| day_per_year | Firmware | PositiveSmallIntegerField | No | 365 | |
| power_cycle_count | Firmware | PositiveIntegerField | No | — | |
| default_rebuild_time | Firmware | PositiveIntegerField | No | — | |
| drive_log_region_size | Firmware | PositiveIntegerField | No | — | |
| drive_log_min_op | Firmware | FloatField | No | — | |
| using_slc_write_cache | Firmware | BooleanField | No | — | |
| using_pmd | Firmware | BooleanField | No | — | |
| min_mapping_op_with_pmd | Firmware | FloatField | No | — | |
| data_open | Firmware | PositiveSmallIntegerField | No | — | |
| data_open_with_slc_wc | Firmware | PositiveSmallIntegerField | No | — | |
| data_gc_damper_central | Firmware | FloatField | No | — | |
| min_pfail_vb | Firmware | PositiveIntegerField | No | — | |
| small_table_vb | Firmware | PositiveIntegerField | No | — | |
| pfail_max_plane_count | Firmware | PositiveSmallIntegerField | No | — | |
| bol_block_number | Firmware | PositiveIntegerField | No | — | |
| extra_table_life_for_align_spec | Firmware | FloatField | No | — | |
| pb_per_disk_by_channel | Channel | JSONField | No | — | `{"2": 100, "4": 200}` |
| journal_insert_time | Journal | PositiveIntegerField | No | — | |
| journal_entry_size | Journal | PositiveIntegerField | No | — | |
| journal_program_unit | Journal | PositiveIntegerField | No | — | |
| created_at | — | DateTimeField | No | auto | from BaseEntity |
| updated_at | — | DateTimeField | No | auto | from BaseEntity |

**NandInstance**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | from BaseEntity |
| nand | FK → Nand | No | — | CASCADE |
| module_capacity | PositiveBigIntegerField | No | — | |
| user_capacity | PositiveBigIntegerField | No | — | |
| namespace_num | PositiveSmallIntegerField | No | — | |
| ns_remap_table_unit | PositiveIntegerField | No | — | |
| data_pca_width | PositiveSmallIntegerField | No | — | |
| l2p_width | PositiveSmallIntegerField | No | — | |
| data_vb_die_ratio | FloatField | No | — | ≤ 1.0 |
| page_num_per_raid_tag | PositiveIntegerField | No | — | |
| p2l_node_per_data_p2l_group | PositiveIntegerField | No | — | |
| data_p2l_group_num | PositiveIntegerField | No | — | |
| table_vb_good_die_ratio | FloatField | No | — | ≤ 1.0 |
| created_at | DateTimeField | No | auto | from BaseEntity |
| updated_at | DateTimeField | No | auto | from BaseEntity |

UNIQUE: `(nand, name)`

**NandPerf**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | from BaseEntity |
| nand | FK → Nand | No | — | CASCADE |
| bandwidth | FloatField | No | — | |
| module_capacity | PositiveBigIntegerField | No | — | |
| channel | PositiveSmallIntegerField | No | — | |
| die_per_channel | PositiveSmallIntegerField | No | — | |
| created_at | DateTimeField | No | auto | from BaseEntity |
| updated_at | DateTimeField | No | auto | from BaseEntity |

---

#### Properties App (`properties` — 7 tables)

**PropertyConfig**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| content_type | FK → ContentType | No | — | CASCADE |
| name | CharField(255) | No | — | |
| display_text | CharField(255) | No | `""` | |
| description | TextField | No | `""` | |
| read_only | BooleanField | No | `false` | |
| is_extended | BooleanField | No | `false` | |
| is_primary | BooleanField | No | `false` | |
| is_numeric | BooleanField | No | `false` | |
| sub_type | CharField(50) | No | `""` | `percent`, `byte`, etc. |
| decimal_place | PositiveSmallIntegerField | Yes | null | |
| unit | CharField(50) | No | `""` | |

UNIQUE: `(content_type, name)`

**PropertyConfigSet**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| content_type | FK → ContentType | No | — | CASCADE |
| name | CharField(255) | No | — | |

UNIQUE: `(content_type, name)`

**PropertyConfigSetMembership** (through model)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| config_set | FK → PropertyConfigSet | No | — | CASCADE |
| config | FK → PropertyConfig | No | — | CASCADE |
| index | PositiveIntegerField | No | — | Display order within set |

UNIQUE: `(config_set, config)`, `(config_set, index)`

**ExtendedPropertySet**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | |
| content_type | FK → ContentType | Yes | null | Optional scoping to a model type |

**ExtendedPropertySetMembership** (junction table)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| property_set | FK → ExtendedPropertySet | No | — | CASCADE |
| extended_property | FK → ExtendedProperty | No | — | CASCADE |
| index | PositiveIntegerField | No | — | Display order within set |

UNIQUE: `(property_set, extended_property)`, `(property_set, index)`

**ExtendedProperty**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| content_type | FK → ContentType | No | — | CASCADE; always required |
| name | CharField(255) | No | — | |
| is_formula | BooleanField | No | — | |
| default_value | JSONField | Yes | null | Fallback for instances with no per-instance value record |

UNIQUE: `(content_type, name)`

> **Usage policy**: Use `ExtendedProperty` only for static or formula-based values (formulas, fixed constants). For values that differ per hardware instance, add a native model field instead.

**ExtendedPropertyValue** (per-instance values via GenericFK)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| extended_property | FK → ExtendedProperty | No | — | CASCADE |
| content_type | FK → ContentType | No | — | GenericFK target type |
| object_id | PositiveIntegerField | No | — | GenericFK target PK |
| value | JSONField | No | — | Formula string or literal |

UNIQUE: `(extended_property, content_type, object_id)`; INDEX: `(content_type, object_id)`

---

#### Results App (`results` — 4 tables)

**ResultProfile**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | UNIQUE |

**ResultWorkload**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | |
| type | IntegerField | No | — | Opaque workload type identifier |

**ResultProfileWorkload** (through model)

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| profile | FK → ResultProfile | No | — | CASCADE |
| workload | FK → ResultWorkload | No | — | CASCADE |
| config_set | FK → PropertyConfigSet | Yes | null | SET_NULL |
| extended_property_set | FK → ExtendedPropertySet | Yes | null | SET_NULL |

UNIQUE: `(profile, workload)`

**ResultRecord**

| Field | Type | Null | Default | Notes |
|-------|------|------|---------|-------|
| id | BigAutoField | No | — | PK |
| name | CharField(255) | No | — | from BaseEntity |
| data | JSONField | Yes | null | Free-form snapshot of hardware/config at record time |
| created_at | DateTimeField | No | auto | from BaseEntity; ordering: `-created_at` |
| updated_at | DateTimeField | No | auto | from BaseEntity |

---

### Table Layout

Actual database tables with example rows. Content is illustrative.

```
cpu_cpu
┌────┬──────────────┬───────────┬────────────┬────────────┐
│ id │ name         │ bandwidth │ created_at │ updated_at │
├────┼──────────────┼───────────┼────────────┼────────────┤
│  1 │ Controller X │   12800.0 │ 2026-03-01 │ 2026-03-01 │
└────┴──────────────┴───────────┴────────────┴────────────┘


dram_dram
┌────┬────────┬───────────┬─────────┬───────────────┬────────────┬────────────┐
│ id │ name   │ bandwidth │ channel │ transfer_rate │ created_at │ updated_at │
├────┼────────┼───────────┼─────────┼───────────────┼────────────┼────────────┤
│  1 │ DDR5-A │   51200.0 │       2 │        6400.0 │ 2026-03-01 │ 2026-03-01 │
└────┴────────┴───────────┴─────────┴───────────────┴────────────┴────────────┘


nand_nand  (45 data fields + timestamps; key columns shown)
┌────┬───────┬──────────────────┬───────────────┬──────────────┬─────┬────────────┬────────────┐
│ id │ name  │ capacity_per_die │ plane_per_die │ day_per_year │ ... │ created_at │ updated_at │
├────┼───────┼──────────────────┼───────────────┼──────────────┼─────┼────────────┼────────────┤
│  1 │ BiCS8 │       1073741824 │             4 │          365 │ ... │ 2026-03-01 │ 2026-03-01 │
│  2 │ BiCS9 │       2147483648 │             6 │          365 │ ... │ 2026-03-01 │ 2026-03-01 │
└────┴───────┴──────────────────┴───────────────┴──────────────┴─────┴────────────┴────────────┘
Fields grouped logically: physical (8), endurance (4), raid (5), mapping (8), firmware (16),
channel (1 JSONField), journal (3). See Field Reference for full list.


nand_nandinstance
┌────┬─────────┬─────────┬─────────────────┬───────────────┬─────┬────────────┬────────────┐
│ id │ name    │ nand_id │ module_capacity │ user_capacity │ ... │ created_at │ updated_at │
├────┼─────────┼─────────┼─────────────────┼───────────────┼─────┼────────────┼────────────┤
│  1 │ 0.5T 7% │       1 │    549755813888 │  512110190592 │ ... │ 2026-03-01 │ 2026-03-01 │
│  2 │ 8T 28%  │       1 │   8796093022208 │ 6332740796416 │ ... │ 2026-03-01 │ 2026-03-01 │
└────┴─────────┴─────────┴─────────────────┴───────────────┴─────┴────────────┴────────────┘
UNIQUE: (nand_id, name)


nand_nandperf
┌────┬─────────┬─────────┬───────────┬─────────────────┬─────────┬─────────────────┬────────────┬────────────┐
│ id │ name    │ nand_id │ bandwidth │ module_capacity │ channel │ die_per_channel │ created_at │ updated_at │
├────┼─────────┼─────────┼───────────┼─────────────────┼─────────┼─────────────────┼────────────┼────────────┤
│  1 │ 4ch cfg │       1 │    3200.0 │    549755813888 │       4 │               8 │ 2026-03-01 │ 2026-03-01 │
│  2 │ 2ch cfg │       1 │    1600.0 │    549755813888 │       2 │              16 │ 2026-03-01 │ 2026-03-01 │
└────┴─────────┴─────────┴───────────┴─────────────────┴─────────┴─────────────────┴────────────┴────────────┘


properties_propertyconfig
┌────┬─────────────────┬──────────────────┬──────────────┬────────────┬──────┐
│ id │ content_type_id │ name             │ display_text │ is_numeric │ unit │
├────┼─────────────────┼──────────────────┼──────────────┼────────────┼──────┤
│  1 │  8 (nand.nand)  │ capacity_per_die │ Cap/Die      │ true       │ B    │
│  2 │  8 (nand.nand)  │ plane_per_die    │ Plane/Die    │ true       │      │
│ .. │             ... │              ... │          ... │ ...        │  ... │
│ 47 │ 10 (cpu.cpu)    │ bandwidth        │ BW           │ true       │ MB/s │
│ 48 │ 11 (dram.dram)  │ bandwidth        │ BW           │ true       │ MB/s │
│ 49 │ 12 (resultwork) │ time             │ Time         │ true       │ ms   │
└────┴─────────────────┴──────────────────┴──────────────┴────────────┴──────┘
UNIQUE: (content_type_id, name). "bandwidth" for Cpu and Dram are separate rows.


properties_propertyconfigset
┌────┬──────────────────────┬──────────────────────────────┐
│ id │ name                 │ content_type_id              │
├────┼──────────────────────┼──────────────────────────────┤
│  1 │ Nand Full View       │  8 (nand.nand)               │
│  2 │ Nand Compact View    │  8 (nand.nand)               │
│  3 │ Cpu Default          │ 10 (cpu.cpu)                 │
│  4 │ Host Write Columns   │ 12 (results.resultworkload)  │
└────┴──────────────────────┴──────────────────────────────┘
UNIQUE: (content_type_id, name)


properties_propertyconfigsetmembership  (M2M through model)
┌────┬───────────────┬───────────────────┬───────┐
│ id │ config_set_id │ config_id         │ index │
├────┼───────────────┼───────────────────┼───────┤
│  1 │ 1 (Nand Full) │  1 (cap/die)      │     0 │
│  2 │ 1 (Nand Full) │  2 (plane/die)    │     1 │
│  3 │ 2 (Nand Comp) │  1 (cap/die)      │     0 │  ← same config, different index per set
│  4 │ 3 (Cpu Def.)  │ 47 (cpu bw)       │     0 │
│  5 │ 4 (Host Wr C) │ 49 (time)         │     0 │
└────┴───────────────┴───────────────────┴───────┘
UNIQUE: (config_set_id, config_id), (config_set_id, index)


properties_extendedpropertyset
┌────┬──────────────────┬──────────────────────────────┐
│ id │ name             │ content_type_id              │
├────┼──────────────────┼──────────────────────────────┤
│  1 │ GC Read / Upper  │ 12 (results.resultworkload)  │
│  2 │ GC Read / Lower  │ 12 (results.resultworkload)  │
│  3 │ Host Write / Up  │ 12 (results.resultworkload)  │
└────┴──────────────────┴──────────────────────────────┘
content_type_id is nullable (optional scoping) but in practice always set — one set per
profile-workload pair. Sets are referenced from results_resultprofileworkload.


properties_extendedpropertysetmembership  (junction table)
┌────┬──────────────────┬──────────────────────┬───────┐
│ id │ property_set_id  │ extended_property_id │ index │
├────┼──────────────────┼──────────────────────┼───────┤
│  1 │ 1 (GC Rd/Up)     │ 3 (time)             │     0 │
│  2 │ 1 (GC Rd/Up)     │ 4 (performance)      │     1 │
│  3 │ 2 (GC Rd/Lo)     │ 3 (time)             │     0 │  ← same property, two sets
│  4 │ 2 (GC Rd/Lo)     │ 4 (performance)      │     1 │
│  5 │ 3 (Host Wr/Up)   │ 3 (time)             │     0 │  ← same property, third set
└────┴──────────────────┴──────────────────────┴───────┘
UNIQUE: (property_set_id, extended_property_id), (property_set_id, index)
One property can belong to multiple sets.


properties_extendedproperty  (definition only — no value column)
┌────┬─────────────────────────┬─────────────┬────────────┬───────────────┐
│ id │ content_type_id         │ name        │ is_formula │ default_value │
├────┼─────────────────────────┼─────────────┼────────────┼───────────────┤
│  1 │  8 (nand.nand)          │ j_per_pu    │ true       │ NULL          │
│  2 │  8 (nand.nand)          │ disk_op     │ true       │ NULL          │
│  3 │ 12 (results.resultwork) │ time        │ true       │ "=E1*F1"      │
│  4 │ 12 (results.resultwork) │ performance │ true       │ NULL          │
└────┴─────────────────────────┴─────────────┴────────────┴───────────────┘
UNIQUE: (content_type_id, name). content_type_id is always required (non-nullable).


properties_extendedpropertyvalue  (per-instance values via GenericFK)
┌────┬──────────────────────┬─────────────────┬───────────┬───────────┐
│ id │ extended_property_id │ content_type_id │ object_id │ value     │
├────┼──────────────────────┼─────────────────┼───────────┼───────────┤
│  1 │ 1 (j_per_pu)         │  8 (nand.nand)  │ 1 (BiCS8) │ "=A1*B1"  │  ← Nand #1's value
│  2 │ 1 (j_per_pu)         │  8 (nand.nand)  │ 2 (BiCS9) │ "=A1*B2"  │  ← Nand #2's value
│  3 │ 3 (time)             │ 12 (resultwork) │ 1         │ "=E2*F2"  │  ← overrides default
└────┴──────────────────────┴─────────────────┴───────────┴───────────┘
UNIQUE: (extended_property_id, content_type_id, object_id)
INDEX: (content_type_id, object_id) — fast lookup of all values for a given instance.


results_resultprofile
┌────┬──────────────────┐
│ id │ name             │
├────┼──────────────────┤
│  1 │ AIPR Upper Bound │
│  2 │ AIPR Lower Bound │
└────┴──────────────────┘
UNIQUE: name


results_resultworkload
┌────┬────────────┬──────┐
│ id │ name       │ type │
├────┼────────────┼──────┤
│  1 │ Host Write │    1 │
│  2 │ GC Read    │    5 │
└────┴────────────┴──────┘


results_resultprofileworkload  (through model)
┌────┬────────────┬──────────────┬─────────────────────────┬──────────────────────────┐
│ id │ profile_id │ workload_id  │ config_set_id           │ extended_property_set_id │
├────┼────────────┼──────────────┼─────────────────────────┼──────────────────────────┤
│  1 │ 1 (Upper)  │ 2 (GC Read)  │ NULL                    │ 1 (GC Read / Upper)      │
│  2 │ 2 (Lower)  │ 2 (GC Read)  │ NULL                    │ 2 (GC Read / Lower)      │
│  3 │ 1 (Upper)  │ 1 (Host Wr)  │ 4 (Host Write Columns)  │ 3 (Host Write / Up)      │
└────┴────────────┴──────────────┴─────────────────────────┴──────────────────────────┘
UNIQUE: (profile_id, workload_id). Same workload in different profiles → different sets.
config_set_id controls which columns the frontend renders for that profile-workload pair.


results_resultrecord
┌────┬─────────────────────┬──────────────────────────────────────────────────┬────────────┬────────────┐
│ id │ name                │ data                                             │ created_at │ updated_at │
├────┼─────────────────────┼──────────────────────────────────────────────────┼────────────┼────────────┤
│  1 │ BiCS8 + DDR5-A base │ {"nand": {"name": "BiCS8"}, "cpu": {...}}        │ 2026-03-01 │ 2026-03-01 │
│  2 │ Quick run           │ NULL                                             │ 2026-03-01 │ 2026-03-01 │
└────┴─────────────────────┴──────────────────────────────────────────────────┴────────────┴────────────┘
data is a free-form JSON snapshot of hardware/config at record time. NULL = empty record.
Ordered by -created_at. No PUT/PATCH (immutable after creation).
```

## API Design

### Hardware Endpoints

Full CRUD (`ModelViewSet`) for each hardware type.


| Endpoint               | Notes                                                |
| ---------------------- | ---------------------------------------------------- |
| `/api/nand/`           | Write: flat field names. Read: nested into 6 groups. |
| `/api/nand-instances/` | Filter: `?nand=<id>`                                 |
| `/api/nand-perf/`      | Filter: `?nand=<id>`                                 |
| `/api/cpu/`            |                                                      |
| `/api/dram/`           |                                                      |


**Nand read/write asymmetry**: POST/PUT/PATCH accept flat field names matching the DB columns. GET responses nest fields into groups: `physical`, `endurance`, `raid`, `mapping`, `firmware`, `journal`, plus `pb_per_disk_by_channel`.

**Optional query parameters on all entity detail endpoints**:

- `?config_set=<id>` — includes PropertyConfigSet data in the response; omitted if not provided
- `?include=extended_properties` — includes per-instance ExtendedPropertyValues; omitted if not provided

### Properties Endpoints


| Endpoint                         | Notes                                               |
| -------------------------------- | --------------------------------------------------- |
| `/api/property-configs/`         | Filter: `?model=<app_label>` (maps to content_type) |
| `/api/config-sets/`              |                                                     |
| `/api/extended-property-sets/`   |                                                     |
| `/api/extended-properties/`      | Filter: `?model=<app_label>`, `?set=<id>`           |
| `/api/extended-property-values/` | Filter: `?model=<app_label>`, `?object_id=<id>`     |


### Results Endpoints


| Endpoint                         | Notes                                                            |
| -------------------------------- | ---------------------------------------------------------------- |
| `/api/result-profiles/`          |                                                                  |
| `/api/result-workloads/`         |                                                                  |
| `/api/result-profile-workloads/` | Filter: `?profile=<id>`                                          |
| `/api/result-records/`           | GET, POST, DELETE only (no PUT/PATCH). Ordered by `-created_at`. |


**Common configuration across all endpoints:**

- URL registration via `DefaultRouter` in each app's `urls.py`
- `PageNumberPagination` with `PAGE_SIZE=20`
- `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`
- `AllowAny` permissions (public API)

## Environment Configuration

Settings are loaded via **django-environ**. The settings module prefers `.env.local` (if it exists) over `.env`, with `overrides=False` so existing environment variables take priority.


| Variable                    | Default                | Description                            |
| --------------------------- | ---------------------- | -------------------------------------- |
| `SECRET_KEY`                | Dev default provided   | Django secret key                      |
| `DEBUG`                     | `True`                 | Debug mode                             |
| `ALLOWED_HOSTS`             | `localhost,127.0.0.1`  | Allowed host headers                   |
| `DATABASE_URL`              | `sqlite:///db.sqlite3` | Database connection URL                |
| `DJANGO_SUPERUSER_USERNAME` | *(none)*               | Auto-create superuser username         |
| `DJANGO_SUPERUSER_PASSWORD` | *(none)*               | Auto-create superuser password         |
| `DJANGO_SUPERUSER_EMAIL`    | `""`                   | Auto-create superuser email (optional) |


**Local development**: When `DATABASE_URL` is unset, Django uses SQLite at `db.sqlite3` in the project root.

**Docker**: `docker-compose.yml` constructs `DATABASE_URL` from `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`. The `entrypoint.sh` script waits for PostgreSQL to become available (30 retries, 2s interval), runs migrations, creates a superuser (if `DJANGO_SUPERUSER_`* vars are set), then executes the container command.

**File conventions**:

- `.env.example` — Template listing all variables. Committed to the repo.
- `.env` — Docker Compose variable substitution (contains `POSTGRES_`*, `SECRET_KEY`, etc.). Gitignored.
- `.env.local` — Local development overrides (no `DATABASE_URL` → SQLite). Gitignored. Preferred over `.env` by settings.

