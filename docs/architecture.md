# Architecture

Last Updated: 2026-02-25

## System Overview

Django REST API for managing NAND-based SSD performance data. Provides full CRUD operations for hardware components (Nand, NandInstance, NandPerf, Cpu, Dram), a property configuration system for customisable result views, an extended property system for per-instance computed formula values, and a results system for recording and linking test outcomes to hardware configurations.

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

16 database tables across 5 Django apps.

### Hardware Apps

`**cpu**` — 1 table

```
Cpu(BaseEntity)
  bandwidth: FloatField
```

`**dram**` — 1 table

```
Dram(BaseEntity)
  bandwidth: FloatField
  channel: PositiveSmallIntegerField
  transfer_rate: FloatField
```

`**nand**` — 3 tables

```
Nand(BaseEntity)
  # Physical (8 fields): capacity_per_die, plane_per_die, block_per_plane,
  #   d1_d2_ratio [≤1.0], page_per_block, slc_page_per_block, node_per_page, finger_per_wl
  # Endurance (4): tlc_qlc_pe, static_slc_pe, table_slc_pe, bad_block_ratio
  # RAID (5): max_data_raid_frame, max_slc_wc_raid_frame, max_table_raid_frame,
  #   data_die_raid, table_die_raid
  # Mapping (8): l2p_unit, mapping_table_size, p2l_entry, with_p2l, p2l_bitmap,
  #   l2p_ecc_data, l2p_ecc_spare, reserved_lca_number
  # Firmware (16): day_per_year [default 365], power_cycle_count, default_rebuild_time,
  #   drive_log_region_size, drive_log_min_op, using_slc_write_cache, using_pmd,
  #   min_mapping_op_with_pmd, data_open, data_open_with_slc_wc, data_gc_damper_central,
  #   min_pfail_vb, small_table_vb, pfail_max_plane_count, bol_block_number,
  #   extra_table_life_for_align_spec
  # Channel (1): pb_per_disk_by_channel: JSONField
  # Journal (3): journal_insert_time, journal_entry_size, journal_program_unit

NandInstance(BaseEntity)
  nand: FK → Nand (CASCADE)
  module_capacity, user_capacity, namespace_num, ns_remap_table_unit
  data_pca_width, l2p_width
  data_vb_die_ratio [≤1.0], page_num_per_raid_tag
  p2l_node_per_data_p2l_group, data_p2l_group_num
  table_vb_good_die_ratio [≤1.0]
  UNIQUE(nand, name)

NandPerf(BaseEntity)
  nand: FK → Nand (CASCADE)
  bandwidth, module_capacity, channel, die_per_channel
```

### Properties App

`**properties**` — 6 tables

```
PropertyConfig
  content_type: FK → ContentType
  name, display_text, description
  read_only, is_extended, is_primary, is_numeric
  sub_type, decimal_place, unit
  UNIQUE(content_type, name)

PropertyConfigSet
  content_type: FK → ContentType
  name
  UNIQUE(content_type, name)

PropertyConfigSetMembership
  config_set: FK → PropertyConfigSet
  config: FK → PropertyConfig
  index: PositiveIntegerField
  UNIQUE(config_set, config), UNIQUE(config_set, index)

ExtendedPropertySet
  name, content_type (nullable FK → ContentType)

ExtendedProperty
  content_type: nullable FK → ContentType  (exactly one binding required)
  property_set: nullable FK → ExtendedPropertySet
  name, is_formula
  default_value: JSONField(null=True)  ← fallback for instances with no per-instance value record
  CHECK: exactly one of (content_type, property_set) is non-null
  UNIQUE(content_type, name) where content_type IS NOT NULL
  UNIQUE(property_set, name) where property_set IS NOT NULL

ExtendedPropertyValue
  extended_property: FK → ExtendedProperty
  content_type: FK → ContentType   (GenericForeignKey target type)
  object_id: PositiveIntegerField  (GenericForeignKey target PK)
  value: TextField
  UNIQUE(extended_property, content_type, object_id)
  INDEX(content_type, object_id)
```

### Results App

`**results**` — 5 tables

```
ResultProfile
  name (unique)

ResultWorkload
  name, type: IntegerField

ResultProfileWorkload  [through model]
  profile: FK → ResultProfile (CASCADE)
  workload: FK → ResultWorkload (CASCADE)
  config_set: nullable FK → PropertyConfigSet (SET_NULL)
  extended_property_set: nullable FK → ExtendedPropertySet (SET_NULL)
  UNIQUE(profile, workload)

ResultRecord(BaseEntity)
  nand: nullable FK → nand.Nand (SET_NULL)
  nand_instance: nullable FK → nand.NandInstance (SET_NULL)
  nand_perf: nullable FK → nand.NandPerf (SET_NULL)
  cpu: nullable FK → cpu.Cpu (SET_NULL)
  dram: nullable FK → dram.Dram (SET_NULL)
  ordering: -created_at

ResultInstance
  result_record: FK → ResultRecord (CASCADE)
  profile_workload: FK → ResultProfileWorkload (CASCADE)
  created_at, updated_at
  UNIQUE(result_record, profile_workload)
```

### BaseEntity (abstract)

```
BaseEntity
  name: CharField(max_length=255)
  created_at: DateTimeField(auto_now_add=True)
  updated_at: DateTimeField(auto_now=True)
```

Inherited by: `Cpu`, `Dram`, `Nand`, `NandInstance`, `NandPerf`, `ResultRecord`.

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
| `/api/extended-properties/`      | Filter: `?model=<app_label>`, `?property_set=<id>`  |
| `/api/extended-property-values/` | Filter: `?model=<app_label>`, `?object_id=<id>`     |


### Results Endpoints


| Endpoint                         | Notes                                                            |
| -------------------------------- | ---------------------------------------------------------------- |
| `/api/result-profiles/`          |                                                                  |
| `/api/result-workloads/`         |                                                                  |
| `/api/result-profile-workloads/` | Filter: `?profile=<id>`                                          |
| `/api/result-records/`           | GET, POST, DELETE only (no PUT/PATCH). Ordered by `-created_at`. |
| `/api/result-instances/`         | GET, POST, DELETE only. Filter: `?result_record=<id>`            |


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

