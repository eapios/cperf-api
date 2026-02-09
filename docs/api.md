# API Reference

Last Updated: 2026-02-09

## Base URL

```
http://localhost:8000
```

**Authentication**: None (all endpoints use `AllowAny`).

## Endpoints

All CRUD endpoints support: search (`?search=`), ordering (`?ordering=`), pagination (`?page=`, 20 per page).

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/components/` | GET | Read-only aggregate view of all components |
| `/api/components/{id}/` | GET | Retrieve single component by UUID |
| `/api/cpu/` | GET, POST | List / create CPU components |
| `/api/cpu/{id}/` | GET, PUT, PATCH, DELETE | Retrieve / update / delete CPU |
| `/api/dram/` | GET, POST | List / create DRAM components |
| `/api/dram/{id}/` | GET, PUT, PATCH, DELETE | Retrieve / update / delete DRAM |

## Components (Read-Only)

Unified view across all component types. Filter by `?component_type=cpu` or `?component_type=dram`.

**Ordering fields**: `created_at`, `name`

## CPU

**Ordering fields**: `created_at`, `name`, `cores`, `clock_speed`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | read-only | Auto-generated |
| name | string | yes | Max 255 chars |
| component_type | string | read-only | Auto-set to `"cpu"` |
| description | string | no | Default `""` |
| cores | positive integer | yes | |
| threads | positive integer | yes | Must be >= `cores` |
| clock_speed | decimal(5,2) | yes | Base clock in GHz |
| boost_clock | decimal(5,2) | no | Must be >= `clock_speed` |
| tdp | positive integer | no | Watts |
| socket | string | no | Max 50 chars |
| created_at | datetime | read-only | |
| updated_at | datetime | read-only | |

## DRAM

**Ordering fields**: `created_at`, `name`, `capacity_gb`, `speed_mhz`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | read-only | Auto-generated |
| name | string | yes | Max 255 chars |
| component_type | string | read-only | Auto-set to `"dram"` |
| description | string | no | Default `""` |
| capacity_gb | positive integer | yes | |
| speed_mhz | positive integer | yes | |
| ddr_type | string | yes | Max 10 chars (e.g. `"DDR5"`) |
| modules | positive integer | no | Default `1` |
| cas_latency | positive integer | no | |
| voltage | decimal(3,2) | no | |
| created_at | datetime | read-only | |
| updated_at | datetime | read-only | |

## Validation

Validation errors return **400** with field-level messages.

- **CPU**: `threads` >= `cores`; `boost_clock` >= `clock_speed` (if provided); `name` not blank
- **DRAM**: `name` not blank

## Pagination

All list endpoints return a paginated envelope:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/cpu/?page=2",
  "previous": null,
  "results": [...]
}
```
