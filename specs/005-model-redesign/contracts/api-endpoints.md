# API Contracts: Backend Model Redesign

**Feature**: 005-model-redesign
**Date**: 2026-02-23

All endpoints use DRF `ModelViewSet` with `DefaultRouter`. Standard CRUD (list, create, retrieve, update, partial_update, destroy).

## Base URL: `/api/`

## Hardware Entities

### Nand Technologies

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/nand/` | List all NAND technologies |
| POST | `/api/nand/` | Create NAND technology |
| GET | `/api/nand/{id}/` | Retrieve NAND (with optional `?config_set=N&include=extended_properties`) |
| PUT | `/api/nand/{id}/` | Update NAND technology |
| PATCH | `/api/nand/{id}/` | Partial update |
| DELETE | `/api/nand/{id}/` | Delete (cascades to instances + perf entries) |

**Response nesting**: Fields grouped into `physical`, `endurance`, `raid`, `mapping`, `firmware`, `journal`, `pb_per_disk_by_channel`.

### Nand Instances

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/nand-instances/` | List all (filterable by `?nand=N`) |
| POST | `/api/nand-instances/` | Create |
| GET | `/api/nand-instances/{id}/` | Retrieve (with optional `?config_set=N&include=extended_properties`) |
| PUT/PATCH | `/api/nand-instances/{id}/` | Update |
| DELETE | `/api/nand-instances/{id}/` | Delete |

### Nand Performance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/nand-perf/` | List all (filterable by `?nand=N`) |
| POST | `/api/nand-perf/` | Create |
| GET | `/api/nand-perf/{id}/` | Retrieve (with optional `?config_set=N&include=extended_properties`) |
| PUT/PATCH | `/api/nand-perf/{id}/` | Update |
| DELETE | `/api/nand-perf/{id}/` | Delete |

### CPU

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/cpu/` | List all CPUs |
| POST | `/api/cpu/` | Create CPU |
| GET | `/api/cpu/{id}/` | Retrieve (with optional `?config_set=N&include=extended_properties`) |
| PUT/PATCH | `/api/cpu/{id}/` | Update |
| DELETE | `/api/cpu/{id}/` | Delete |

### DRAM

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dram/` | List all DRAMs |
| POST | `/api/dram/` | Create DRAM |
| GET | `/api/dram/{id}/` | Retrieve (with optional `?config_set=N&include=extended_properties`) |
| PUT/PATCH | `/api/dram/{id}/` | Update |
| DELETE | `/api/dram/{id}/` | Delete |

## Properties System

### Property Configs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/property-configs/` | List all (filterable by `?model=nand`) |
| POST | `/api/property-configs/` | Create |
| GET | `/api/property-configs/{id}/` | Retrieve |
| PUT/PATCH | `/api/property-configs/{id}/` | Update |
| DELETE | `/api/property-configs/{id}/` | Delete |

### Property Config Sets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/config-sets/` | List all (filterable by `?model=nand`) |
| POST | `/api/config-sets/` | Create (with nested memberships) |
| GET | `/api/config-sets/{id}/` | Retrieve with ordered config items |
| PUT/PATCH | `/api/config-sets/{id}/` | Update |
| DELETE | `/api/config-sets/{id}/` | Delete |

### Extended Property Sets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/extended-property-sets/` | List all sets |
| POST | `/api/extended-property-sets/` | Create (for entity-level sets, pass `content_type`; for result-level sets, leave `content_type` null) |
| GET | `/api/extended-property-sets/{id}/` | Retrieve |
| PUT/PATCH | `/api/extended-property-sets/{id}/` | Update |
| DELETE | `/api/extended-property-sets/{id}/` | Delete |

### Extended Properties (Definitions)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/extended-properties/` | List all (filterable by `?model=nand` or `?property_set=N`) |
| POST | `/api/extended-properties/` | Create definition |
| GET | `/api/extended-properties/{id}/` | Retrieve |
| PUT/PATCH | `/api/extended-properties/{id}/` | Update |
| DELETE | `/api/extended-properties/{id}/` | Delete (cascades values) |

### Extended Property Values

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/extended-property-values/` | List (filterable by `?model=nand&object_id=1`) |
| POST | `/api/extended-property-values/` | Create per-instance value |
| GET | `/api/extended-property-values/{id}/` | Retrieve |
| PUT/PATCH | `/api/extended-property-values/{id}/` | Update value |
| DELETE | `/api/extended-property-values/{id}/` | Delete |

## Results System

### Result Profiles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/result-profiles/` | List all profiles |
| POST | `/api/result-profiles/` | Create |
| GET | `/api/result-profiles/{id}/` | Retrieve with nested workloads, instances, and values |
| PUT/PATCH | `/api/result-profiles/{id}/` | Update |
| DELETE | `/api/result-profiles/{id}/` | Delete |

### Result Workloads

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/result-workloads/` | List all workloads |
| POST | `/api/result-workloads/` | Create |
| GET | `/api/result-workloads/{id}/` | Retrieve |
| PUT/PATCH | `/api/result-workloads/{id}/` | Update |
| DELETE | `/api/result-workloads/{id}/` | Delete |

### Result Profile Workloads (Linkage)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/result-profile-workloads/` | List (filterable by `?profile=N`) |
| POST | `/api/result-profile-workloads/` | Link workload to profile |
| DELETE | `/api/result-profile-workloads/{id}/` | Unlink |

### Result Records

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/result-records/` | List all records (ordered by -created_at) |
| POST | `/api/result-records/` | Save a calculation run (with hardware FKs) |
| GET | `/api/result-records/{id}/` | Retrieve with nested instances and values |
| DELETE | `/api/result-records/{id}/` | Delete (cascades instances) |

### Result Instances

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/result-instances/` | List (filterable by `?result_record=N`) |
| POST | `/api/result-instances/` | Create |
| GET | `/api/result-instances/{id}/` | Retrieve with extended property values |
| DELETE | `/api/result-instances/{id}/` | Delete |

## Common Query Parameters

| Parameter | Applies To | Description |
|-----------|-----------|-------------|
| `?config_set=<id>` | Entity detail endpoints | Include PropertyConfigSet in response |
| `?include=extended_properties` | Entity detail endpoints | Include per-instance ExtendedPropertyValues |
| `?model=<app_label>` | Config/property list endpoints | Filter by model type |
| `?nand=<id>` | NandInstance, NandPerf list | Filter by parent Nand |
| `?profile=<id>` | ResultProfileWorkload list | Filter by profile |
| `?result_record=<id>` | ResultInstance list | Filter by record |

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | Deleted (DELETE) |
| 400 | Validation error (field types, constraints) |
| 404 | Not found |
