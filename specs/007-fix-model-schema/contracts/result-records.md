# Contract: Result Records API

**Changed endpoints** — FR-001, FR-004

## POST /api/result-records/

**Request**
```json
{
  "name": "run-001",
  "data": { "nand": { "name": "BiCS8", "capacity_per_die": 1099511627776 }, "cpu": { "name": "A100" } }
}
```
`data` is optional; omitting it or passing `null` is valid.

**Response 201**
```json
{
  "id": 1,
  "name": "run-001",
  "data": { "nand": { "name": "BiCS8", "capacity_per_die": 1099511627776 }, "cpu": { "name": "A100" } },
  "created_at": "2026-03-02T00:00:00Z",
  "updated_at": "2026-03-02T00:00:00Z"
}
```

**Removed fields from response**: `nand`, `nand_instance`, `nand_perf`, `cpu`, `dram`

---

## GET /api/result-records/

Returns paginated list. Fields same as POST 201 response.

## GET /api/result-records/{id}/

Same fields as POST 201 response.

## DELETE /api/result-records/{id}/

**Response 204** — no body.

---

## REMOVED: /api/result-instances/

Endpoint removed entirely (FR-003). Any calls return 404.
