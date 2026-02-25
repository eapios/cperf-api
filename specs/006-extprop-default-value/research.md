# Research: Extended Property Default Value

**Branch**: `006-extprop-default-value` | **Phase**: 0

## Decision Log

### D-001: Field Type for `default_value`

**Decision**: `models.JSONField(null=True, blank=True, default=None)`

**Rationale**: `ExtendedPropertyValue.value` is already a `JSONField`. Using the same type ensures identical semantics (accepts text, number, boolean, null, list, dict). `null=True` encodes "no default defined" per FR-002. `blank=True` allows empty POSTs without providing the field.

**Alternatives considered**:
- `TextField` — rejected; loses numeric/boolean type fidelity for callers.
- Separate `default_value_type` discriminator column — rejected; YAGNI, callers already interpret `ExtendedPropertyValue.value` without a type hint.

---

### D-002: Resolution API Shape

**Decision**: Custom `@action` on `ExtendedPropertyViewSet`:

```
GET /api/properties/extended-properties/{id}/resolve/?model=<app_label>&object_id=<pk>
```

Response:
```json
{ "property_id": 5, "value": 65, "is_default": true }
```

**Rationale**: SC-002 requires "no additional steps required by the caller" — a single endpoint that returns the resolved value (per-instance or default) satisfies this. Placing it as an action on the property resource is RESTful and avoids a new top-level endpoint.

**Alternatives considered**:
- New standalone `/resolve/` viewset — rejected; unnecessary endpoint proliferation for a single-action concern.
- Enrich the existing value list with "missing" entries padded with defaults — rejected; changes contract of the value list endpoint and adds complexity.
- No server-side resolution (client does two queries) — rejected; violates SC-002.

---

### D-003: Migration Safety

**Decision**: Simple `AddField` migration with `null=True` — no data backfill needed.

**Rationale**: The spec explicitly states "all existing `ExtendedProperty` records will have `default_value = null` after the migration." `null=True` allows the DB column to be added with no default without touching existing rows.

**Alternatives considered**:
- Provide a non-null default (e.g., `""`) — rejected; null carries explicit meaning ("no default defined") per FR-002.

---

### D-004: Serializer field exposure

**Decision**: Add `default_value` to `ExtendedPropertySerializer.fields` list. No special validation required beyond what `JSONField` provides.

**Rationale**: The field must be settable and updatable via the standard property management interface (FR-006). The existing serializer already validates the `content_type`/`property_set` mutual exclusivity; `default_value` requires no additional cross-field validation.

---

### D-005: Formula property behaviour

**Decision**: No special handling for `is_formula=True` properties — `default_value` stores and returns the value as-is.

**Rationale**: Spec assumption: "The feature does not add logic to evaluate formula defaults; it only stores and returns the formula string, consistent with how per-instance formula values are handled today." This avoids scope creep.
