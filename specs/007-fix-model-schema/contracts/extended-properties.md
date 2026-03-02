# Contract: Extended Properties API

**Changed endpoints** — FR-006, FR-007, FR-008

---

## ExtendedProperty

### POST /api/extended-properties/

**Request**
```json
{
  "content_type": 5,
  "name": "TDP",
  "is_formula": false,
  "default_value": 65
}
```

`content_type` is **required**. `property_set` field no longer exists.

**Response 201**
```json
{
  "id": 1,
  "content_type": 5,
  "name": "TDP",
  "is_formula": false,
  "default_value": 65
}
```

**Removed fields**: `property_set`

**Error 400** — content_type missing or null:
```json
{ "content_type": ["This field is required."] }
```

### GET /api/extended-properties/

Query params:
- `?model=<app_label>` — filter by content type app label
- `?set=<set_id>` — **NEW**: filter properties that belong to a given ExtendedPropertySet (via membership)

### GET /api/extended-properties/{id}/resolve/?model=&object_id=

Unchanged. Returns `{ property_id, value, is_default }`.

---

## ExtendedPropertySet

### GET /api/extended-property-sets/{id}/

Response now includes nested `items`:

```json
{
  "id": 1,
  "name": "Result Props",
  "content_type": null,
  "items": [
    {
      "id": 1,
      "index": 0,
      "extended_property": {
        "id": 3,
        "content_type": 7,
        "name": "Latency",
        "is_formula": true,
        "default_value": "=A/B"
      }
    }
  ]
}
```

---

## ExtendedPropertySetMembership (NEW — FR-008)

### GET /api/extended-property-set-memberships/

Returns list of memberships.

### POST /api/extended-property-set-memberships/

**Request**
```json
{
  "property_set_id": 1,
  "extended_property_id": 3,
  "index": 0
}
```

**Response 201**
```json
{
  "id": 1,
  "index": 0,
  "extended_property": {
    "id": 3,
    "content_type": 7,
    "name": "Latency",
    "is_formula": true,
    "default_value": "=A/B"
  }
}
```

**Error 400** — duplicate `(property_set, extended_property)` or `(property_set, index)`:
```json
{ "non_field_errors": ["The fields property_set, extended_property must make a unique set."] }
```

### DELETE /api/extended-property-set-memberships/{id}/

**Response 204** — no body.

No PUT/PATCH — memberships are deleted and recreated (same as PropertyConfigSetMembership).
