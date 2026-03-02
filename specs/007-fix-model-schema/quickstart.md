# Quickstart: Model Schema Fixes

**Branch**: `007-fix-model-schema`

## Changes at a glance

| Area | What changes |
|---|---|
| `results/models.py` | Remove `ResultInstance`; strip FK fields from `ResultRecord`; add `data` JSONField |
| `results/serializers.py` | Remove `ResultInstanceSerializer`; update `ResultRecordSerializer` fields |
| `results/views.py` | Remove `ResultInstanceFilter` + `ResultInstanceViewSet` |
| `results/urls.py` | Remove `result-instances` router registration |
| `properties/models.py` | Add `ExtendedPropertySetMembership`; remove `property_set` from `ExtendedProperty`; make `content_type` non-nullable |
| `properties/serializers.py` | Add `ExtendedPropertySetMembershipSerializer`; update `ExtendedPropertySetSerializer` (add `items`); update `ExtendedPropertySerializer` (remove `property_set`) |
| `properties/views.py` | Add `ExtendedPropertySetMembershipViewSet`; update `ExtendedPropertyFilter` (`set` filter replaces `property_set`) |
| `properties/urls.py` | Register `extended-property-set-memberships` |
| `properties/admin.py` | Register `ExtendedPropertySetMembership` |
| `results/migrations/0002_*` | Drop ResultInstance + FK columns; add `data` JSONField |
| `properties/migrations/0003_*` | Create membership table; data-migrate; clean up; alter ExtendedProperty |
| `tests/test_results_api.py` | Delete `TestResultInstance`; rewrite `TestResultRecord` |
| `tests/test_extended_props.py` | Rewrite `TestExtendedPropertyBinding` + `TestResultLevelPropertyResolve` |
| `docs/` | Update architecture.md, api.md, models.ts, CHANGELOG.md |

## Run after implementation

```bash
python manage.py makemigrations   # verify 0002 (results) and 0003 (properties) look correct
python manage.py migrate
pytest
ruff check .
black .
```
