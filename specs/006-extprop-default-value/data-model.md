# Data Model: Extended Property Default Value

**Branch**: `006-extprop-default-value` | **Phase**: 1

## Entities Changed

### ExtendedProperty (modified)

| Field | Type | Null | Default | Notes |
|---|---|---|---|---|
| `id` | BigAutoField | No | auto | PK (unchanged) |
| `content_type` | FK → ContentType | Yes | — | Entity-level binding (unchanged) |
| `property_set` | FK → ExtendedPropertySet | Yes | — | Result-level binding (unchanged) |
| `name` | CharField(255) | No | — | (unchanged) |
| `is_formula` | BooleanField | No | False | (unchanged) |
| **`default_value`** | **JSONField** | **Yes** | **None** | **NEW — fallback value for instances without a per-instance record** |

**New field**:
```python
default_value = models.JSONField(null=True, blank=True, default=None)
```

**Semantic contract**:
- `null` → no default defined; instances without a value record have no fallback.
- any JSON-compatible value → used as fallback for instances without a per-instance `ExtendedPropertyValue`.

### ExtendedPropertyValue (unchanged)

No changes. The per-instance value table continues to take precedence over `ExtendedProperty.default_value` when a record exists.

## Entities Unchanged

- `PropertyConfig`
- `PropertyConfigSet`
- `PropertyConfigSetMembership`
- `ExtendedPropertySet`

## Resolution Logic (server-side, new)

```
resolve(property_id, content_type, object_id):
    try:
        return ExtendedPropertyValue.objects.get(
            extended_property_id=property_id,
            content_type=content_type,
            object_id=object_id
        ).value, is_default=False
    except ExtendedPropertyValue.DoesNotExist:
        return ExtendedProperty.objects.get(pk=property_id).default_value, is_default=True
```

## Migration

New migration `0002_extendedproperty_default_value`:
- `AddField(model_name='extendedproperty', name='default_value', field=JSONField(null=True, blank=True, default=None))`
- No data migration required.
