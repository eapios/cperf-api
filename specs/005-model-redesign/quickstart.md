# Quickstart: Backend Model Redesign

**Feature**: 005-model-redesign
**Date**: 2026-02-23

## Prerequisites

- Python 3.12+
- Dependencies installed: `pip install -r requirements/dev.txt`
- Database: SQLite (local) or PostgreSQL 16 (Docker)

## Implementation Order

### Phase 1: Foundation (P1 — Migration + Base Models)

1. Create `properties/` app with `BaseEntity` abstract model
2. Rewrite `cpu/models.py` — replace `CpuComponent` with `Cpu(BaseEntity)`
3. Rewrite `dram/models.py` — replace `DramComponent` with `Dram(BaseEntity)`
4. Create `nand/` app with Nand, NandInstance, NandPerf models
5. Delete `components/` app entirely
6. Update `config/settings.py` — INSTALLED_APPS
7. Run `makemigrations` + `migrate`
8. Rewrite serializers/views/urls for cpu, dram, nand
9. Update `config/urls.py`
10. Rewrite tests

### Phase 2: Properties System (P2)

1. Add PropertyConfig, PropertyConfigSet, PropertyConfigSetMembership models
2. Add ExtendedPropertySet, ExtendedProperty, ExtendedPropertyValue models
3. Add serializers/views/urls for properties
4. Update entity serializers with `?config_set` and `?include=extended_properties` support
5. Add tests

### Phase 3: Results System (P3)

1. Add ResultProfile, ResultWorkload, ResultProfileWorkload models
2. Add ResultRecord, ResultInstance models
3. Add serializers/views/urls for results
4. Add tests

## Key Commands

```bash
# Run migrations
python manage.py makemigrations properties nand cpu dram results
python manage.py migrate

# Run tests
pytest

# Check types/lint
ruff check .

# Run dev server
python manage.py runserver
```

## Verification

After implementation, verify:

1. `python manage.py showmigrations` — all applied
2. `python manage.py shell` — import all models without errors
3. `pytest` — all tests pass
4. Create a Nand via API → create ExtendedProperty → set per-instance values → retrieve with `?include=extended_properties`
5. Create ResultProfile + Workload → link → create ResultRecord → create ResultInstance → set values
