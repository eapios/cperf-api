# API Reference

Last Updated: 2026-02-09

---

## Base URL

```
http://localhost:8000
```

**Authentication**: None required. All endpoints use `AllowAny` permission.

**Global Filter Backends**: `DjangoFilterBackend`, `OrderingFilter`, `SearchFilter`

---

## Pagination

All list endpoints use `PageNumberPagination` with **20 items per page**.

Navigate pages with the `?page=N` query parameter.

Response envelope:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/components/?page=3",
  "previous": "http://localhost:8000/api/components/?page=1",
  "results": [...]
}
```

---

## Components (Read-Only)

**Prefix**: `/api/components/`

The components endpoint provides a unified read-only view across all hardware component types.

**ViewSet**: `ListModelMixin` + `RetrieveModelMixin` (`GenericViewSet`) -- no create, update, or delete operations.

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/api/components/` | 200 |
| GET | `/api/components/{id}/` | 200, 404 |
| POST/PUT/PATCH/DELETE | `/api/components/` or `/api/components/{id}/` | 405 Method Not Allowed |

**Filterset fields**: `component_type`
**Search fields**: `name`
**Ordering fields**: `created_at`, `name`

### Component Object

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "14th Gen Intel Core desktop processor",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

### List Components

```bash
curl http://localhost:8000/api/components/
```

Filter by type:

```bash
curl "http://localhost:8000/api/components/?component_type=cpu"
```

Search by name:

```bash
curl "http://localhost:8000/api/components/?search=Intel"
```

Order by name:

```bash
curl "http://localhost:8000/api/components/?ordering=name"
```

### Retrieve Component

```bash
curl http://localhost:8000/api/components/550e8400-e29b-41d4-a716-446655440000/
```

**Response (200)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "14th Gen Intel Core desktop processor",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

**Response (404)**:

```json
{
  "detail": "Not found."
}
```

---

## CPU (Full CRUD)

**Prefix**: `/api/cpu/`

**ViewSet**: `ModelViewSet`
**Search fields**: `name`
**Ordering fields**: `created_at`, `name`, `cores`, `clock_speed`

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/api/cpu/` | 200 |
| POST | `/api/cpu/` | 201 |
| GET | `/api/cpu/{id}/` | 200, 404 |
| PUT | `/api/cpu/{id}/` | 200, 404 |
| PATCH | `/api/cpu/{id}/` | 200, 404 |
| DELETE | `/api/cpu/{id}/` | 204, 404 |

### CPU Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | read-only | Auto-generated |
| name | string | yes | Max 255 chars, must not be blank |
| component_type | string | read-only | Auto-set to `"cpu"` |
| description | string | no | Default `""` |
| cores | positive integer | yes | |
| threads | positive integer | yes | Must be >= `cores` |
| clock_speed | decimal(5,2) | yes | Base clock in GHz |
| boost_clock | decimal(5,2) | no | Must be >= `clock_speed` |
| tdp | positive integer | no | Thermal design power in watts |
| socket | string | no | Max 50 chars, default `""` |
| created_at | datetime | read-only | ISO 8601 |
| updated_at | datetime | read-only | ISO 8601 |

### Create CPU

```bash
curl -X POST http://localhost:8000/api/cpu/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Intel Core i9-14900K",
    "description": "14th Gen Intel Core desktop processor",
    "cores": 24,
    "threads": 32,
    "clock_speed": "3.20",
    "boost_clock": "6.00",
    "tdp": 253,
    "socket": "LGA1700"
  }'
```

**Response (201)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "14th Gen Intel Core desktop processor",
  "cores": 24,
  "threads": 32,
  "clock_speed": "3.20",
  "boost_clock": "6.00",
  "tdp": 253,
  "socket": "LGA1700",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

### List CPUs

```bash
curl http://localhost:8000/api/cpu/
```

**Response (200)**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Intel Core i9-14900K",
      "component_type": "cpu",
      "description": "14th Gen Intel Core desktop processor",
      "cores": 24,
      "threads": 32,
      "clock_speed": "3.20",
      "boost_clock": "6.00",
      "tdp": 253,
      "socket": "LGA1700",
      "created_at": "2026-02-09T12:00:00Z",
      "updated_at": "2026-02-09T12:00:00Z"
    }
  ]
}
```

### Retrieve CPU

```bash
curl http://localhost:8000/api/cpu/550e8400-e29b-41d4-a716-446655440000/
```

**Response (200)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "14th Gen Intel Core desktop processor",
  "cores": 24,
  "threads": 32,
  "clock_speed": "3.20",
  "boost_clock": "6.00",
  "tdp": 253,
  "socket": "LGA1700",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

**Response (404)**:

```json
{
  "detail": "Not found."
}
```

### Full Update CPU (PUT)

All required fields must be provided.

```bash
curl -X PUT http://localhost:8000/api/cpu/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Intel Core i9-14900K",
    "description": "Updated description",
    "cores": 24,
    "threads": 32,
    "clock_speed": "3.20",
    "boost_clock": "6.00",
    "tdp": 253,
    "socket": "LGA1700"
  }'
```

**Response (200)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "Updated description",
  "cores": 24,
  "threads": 32,
  "clock_speed": "3.20",
  "boost_clock": "6.00",
  "tdp": 253,
  "socket": "LGA1700",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:05:00Z"
}
```

### Partial Update CPU (PATCH)

Only the fields being changed need to be provided.

```bash
curl -X PATCH http://localhost:8000/api/cpu/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Content-Type: application/json" \
  -d '{
    "boost_clock": "6.20"
  }'
```

**Response (200)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Intel Core i9-14900K",
  "component_type": "cpu",
  "description": "Updated description",
  "cores": 24,
  "threads": 32,
  "clock_speed": "3.20",
  "boost_clock": "6.20",
  "tdp": 253,
  "socket": "LGA1700",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:10:00Z"
}
```

### Delete CPU

```bash
curl -X DELETE http://localhost:8000/api/cpu/550e8400-e29b-41d4-a716-446655440000/
```

**Response (204)**: No content.

**Response (404)**:

```json
{
  "detail": "Not found."
}
```

---

## DRAM (Full CRUD)

**Prefix**: `/api/dram/`

**ViewSet**: `ModelViewSet`
**Search fields**: `name`
**Ordering fields**: `created_at`, `name`, `capacity_gb`, `speed_mhz`

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/api/dram/` | 200 |
| POST | `/api/dram/` | 201 |
| GET | `/api/dram/{id}/` | 200, 404 |
| PUT | `/api/dram/{id}/` | 200, 404 |
| PATCH | `/api/dram/{id}/` | 200, 404 |
| DELETE | `/api/dram/{id}/` | 204, 404 |

### DRAM Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | read-only | Auto-generated |
| name | string | yes | Max 255 chars, must not be blank |
| component_type | string | read-only | Auto-set to `"dram"` |
| description | string | no | Default `""` |
| capacity_gb | positive integer | yes | Capacity in GB |
| speed_mhz | positive integer | yes | Speed in MHz |
| ddr_type | string | yes | Max 10 chars, e.g. `"DDR5"` |
| modules | positive integer | no | Default `1` |
| cas_latency | positive integer | no | CAS latency |
| voltage | decimal(3,2) | no | Operating voltage |
| created_at | datetime | read-only | ISO 8601 |
| updated_at | datetime | read-only | ISO 8601 |

### Create DRAM

```bash
curl -X POST http://localhost:8000/api/dram/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "G.Skill Trident Z5 RGB",
    "description": "High-performance DDR5 desktop memory",
    "capacity_gb": 32,
    "speed_mhz": 6000,
    "ddr_type": "DDR5",
    "modules": 2,
    "cas_latency": 30,
    "voltage": "1.35"
  }'
```

**Response (201)**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "G.Skill Trident Z5 RGB",
  "component_type": "dram",
  "description": "High-performance DDR5 desktop memory",
  "capacity_gb": 32,
  "speed_mhz": 6000,
  "ddr_type": "DDR5",
  "modules": 2,
  "cas_latency": 30,
  "voltage": "1.35",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

### List DRAM

```bash
curl http://localhost:8000/api/dram/
```

**Response (200)**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "G.Skill Trident Z5 RGB",
      "component_type": "dram",
      "description": "High-performance DDR5 desktop memory",
      "capacity_gb": 32,
      "speed_mhz": 6000,
      "ddr_type": "DDR5",
      "modules": 2,
      "cas_latency": 30,
      "voltage": "1.35",
      "created_at": "2026-02-09T12:00:00Z",
      "updated_at": "2026-02-09T12:00:00Z"
    }
  ]
}
```

### Retrieve DRAM

```bash
curl http://localhost:8000/api/dram/660e8400-e29b-41d4-a716-446655440001/
```

**Response (200)**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "G.Skill Trident Z5 RGB",
  "component_type": "dram",
  "description": "High-performance DDR5 desktop memory",
  "capacity_gb": 32,
  "speed_mhz": 6000,
  "ddr_type": "DDR5",
  "modules": 2,
  "cas_latency": 30,
  "voltage": "1.35",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:00:00Z"
}
```

**Response (404)**:

```json
{
  "detail": "Not found."
}
```

### Full Update DRAM (PUT)

All required fields must be provided.

```bash
curl -X PUT http://localhost:8000/api/dram/660e8400-e29b-41d4-a716-446655440001/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "G.Skill Trident Z5 RGB",
    "description": "Updated DDR5 memory description",
    "capacity_gb": 32,
    "speed_mhz": 6400,
    "ddr_type": "DDR5",
    "modules": 2,
    "cas_latency": 32,
    "voltage": "1.40"
  }'
```

**Response (200)**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "G.Skill Trident Z5 RGB",
  "component_type": "dram",
  "description": "Updated DDR5 memory description",
  "capacity_gb": 32,
  "speed_mhz": 6400,
  "ddr_type": "DDR5",
  "modules": 2,
  "cas_latency": 32,
  "voltage": "1.40",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:05:00Z"
}
```

### Partial Update DRAM (PATCH)

Only the fields being changed need to be provided.

```bash
curl -X PATCH http://localhost:8000/api/dram/660e8400-e29b-41d4-a716-446655440001/ \
  -H "Content-Type: application/json" \
  -d '{
    "speed_mhz": 6400
  }'
```

**Response (200)**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "G.Skill Trident Z5 RGB",
  "component_type": "dram",
  "description": "Updated DDR5 memory description",
  "capacity_gb": 32,
  "speed_mhz": 6400,
  "ddr_type": "DDR5",
  "modules": 2,
  "cas_latency": 32,
  "voltage": "1.40",
  "created_at": "2026-02-09T12:00:00Z",
  "updated_at": "2026-02-09T12:10:00Z"
}
```

### Delete DRAM

```bash
curl -X DELETE http://localhost:8000/api/dram/660e8400-e29b-41d4-a716-446655440001/
```

**Response (204)**: No content.

**Response (404)**:

```json
{
  "detail": "Not found."
}
```

---

## Validation Rules

Validation errors return **400 Bad Request** with field-level error messages.

### CPU Validation

- `threads` must be greater than or equal to `cores`
- `boost_clock` (if provided) must be greater than or equal to `clock_speed`
- `name` must not be blank

**Example -- threads less than cores:**

```bash
curl -X POST http://localhost:8000/api/cpu/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bad CPU",
    "cores": 8,
    "threads": 4,
    "clock_speed": "3.50"
  }'
```

**Response (400)**:

```json
{
  "threads": ["Threads must be greater than or equal to cores."]
}
```

**Example -- boost_clock less than clock_speed:**

```bash
curl -X POST http://localhost:8000/api/cpu/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bad CPU",
    "cores": 8,
    "threads": 16,
    "clock_speed": "3.50",
    "boost_clock": "2.00"
  }'
```

**Response (400)**:

```json
{
  "boost_clock": ["Boost clock must be greater than or equal to base clock speed."]
}
```

### DRAM Validation

- `name` must not be blank

**Example -- blank name:**

```bash
curl -X POST http://localhost:8000/api/dram/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "capacity_gb": 16,
    "speed_mhz": 3200,
    "ddr_type": "DDR4"
  }'
```

**Response (400)**:

```json
{
  "name": ["This field may not be blank."]
}
```

---

## Query Parameters

All list endpoints support the following query parameters via the global filter backends.

### Search

Full-text search on the `name` field.

```bash
curl "http://localhost:8000/api/cpu/?search=Intel"
curl "http://localhost:8000/api/dram/?search=Trident"
curl "http://localhost:8000/api/components/?search=Intel"
```

### Ordering

Sort results by allowed fields. Prefix with `-` for descending order.

```bash
# CPU: order by cores descending
curl "http://localhost:8000/api/cpu/?ordering=-cores"

# DRAM: order by speed ascending
curl "http://localhost:8000/api/dram/?ordering=speed_mhz"

# Components: order by name ascending
curl "http://localhost:8000/api/components/?ordering=name"

# Descending order
curl "http://localhost:8000/api/cpu/?ordering=-created_at"
```

**Allowed ordering fields per endpoint:**

| Endpoint | Fields |
|----------|--------|
| `/api/components/` | `created_at`, `name` |
| `/api/cpu/` | `created_at`, `name`, `cores`, `clock_speed` |
| `/api/dram/` | `created_at`, `name`, `capacity_gb`, `speed_mhz` |

### Component Type Filter

Only available on the components endpoint.

```bash
curl "http://localhost:8000/api/components/?component_type=cpu"
curl "http://localhost:8000/api/components/?component_type=dram"
```

### Pagination

Navigate through paginated results (20 items per page).

```bash
# First page (default)
curl http://localhost:8000/api/cpu/

# Second page
curl "http://localhost:8000/api/cpu/?page=2"
```

### Combining Parameters

Query parameters can be combined freely.

```bash
curl "http://localhost:8000/api/cpu/?search=Intel&ordering=-cores&page=1"
curl "http://localhost:8000/api/components/?component_type=cpu&search=Intel&ordering=name"
```
