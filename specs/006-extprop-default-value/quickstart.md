# Quickstart: Extended Property Default Value

**Branch**: `006-extprop-default-value`

## What This Feature Does

Adds a `default_value` field to `ExtendedProperty` so instances without a per-instance value record automatically receive a fallback value. A single `resolve` endpoint returns the effective value without requiring two client calls.

## Files to Change

| File | Change |
|---|---|
| `properties/models.py` | Add `default_value = models.JSONField(null=True, blank=True, default=None)` to `ExtendedProperty` |
| `properties/migrations/0002_extendedproperty_default_value.py` | New migration (auto-generated) |
| `properties/serializers.py` | Add `"default_value"` to `ExtendedPropertySerializer.Meta.fields` |
| `properties/views.py` | Add `resolve` action to `ExtendedPropertyViewSet` |
| `tests/test_extended_props.py` | New test cases (see below) |
| `docs/api.md` | Document new field and endpoint |
| `docs/architecture.md` | Update ExtendedProperty data model table |
| `docs/models.ts` | Add `defaultValue` to `ExtendedProperty` interface |
| `CHANGELOG.md` | Add entry under `[Unreleased]` |

## Implement Step-by-Step

### 1. Model

```python
# properties/models.py — ExtendedProperty class
default_value = models.JSONField(
    null=True, blank=True, default=None,
    help_text="Fallback value for instances with no per-instance value record",
)
```

### 2. Migration

```bash
python manage.py makemigrations properties --name extendedproperty_default_value
```

### 3. Serializer

```python
# ExtendedPropertySerializer.Meta
fields = ["id", "content_type", "property_set", "name", "is_formula", "default_value"]
```

### 4. Resolve Action

```python
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Inside ExtendedPropertyViewSet:
@action(detail=True, methods=["get"], url_path="resolve")
def resolve(self, request, pk=None):
    prop = self.get_object()
    model = request.query_params.get("model")
    object_id = request.query_params.get("object_id")
    if not model or not object_id:
        return Response(
            {"detail": "'model' and 'object_id' query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        ct = ContentType.objects.get(app_label=model)
    except ContentType.DoesNotExist:
        return Response({"detail": "Unknown model."}, status=status.HTTP_404_NOT_FOUND)
    try:
        val = prop.values.get(content_type=ct, object_id=int(object_id)).value
        is_default = False
    except ExtendedPropertyValue.DoesNotExist:
        val = prop.default_value
        is_default = True
    return Response({"property_id": prop.pk, "value": val, "is_default": is_default})
```

## Test Scenarios

```python
# tests/test_extended_props.py

# Scenario 1: Default returned when no per-instance record
# Given: ExtendedProperty(default_value=65), no ExtendedPropertyValue for instance
# Expect: GET /resolve/?model=cpu&object_id=1 → {"value": 65, "is_default": true}

# Scenario 2: Per-instance value overrides default
# Given: ExtendedProperty(default_value=0), ExtendedPropertyValue(value=125) for instance A
# Expect: GET /resolve/?model=cpu&object_id=A → {"value": 125, "is_default": false}
# Expect: GET /resolve/?model=cpu&object_id=B → {"value": 0, "is_default": true}

# Scenario 3: null default_value
# Given: ExtendedProperty(default_value=null), no per-instance record
# Expect: GET /resolve/... → {"value": null, "is_default": true}

# Scenario 4: CRUD — default_value persisted via POST/PATCH
# POST with default_value="TBD" → GET returns default_value="TBD"
# PATCH default_value=0 → GET returns default_value=0

# Scenario 5: Missing query params → 400
# GET /resolve/ (no model/object_id) → 400
```

## Verification

```bash
pytest tests/test_extended_props.py -v
pytest --tb=short   # full suite — no regressions
```
