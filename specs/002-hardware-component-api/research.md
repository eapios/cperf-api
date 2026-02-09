# Research: Hardware Component API & Project Restructure

**Feature Branch**: `002-hardware-component-api`
**Date**: 2026-02-09

## R-001: Model Inheritance Strategy for Multi-App Components

- **Decision**: Django built-in multi-table inheritance. `components.Component` is a concrete base model. Each type-specific app (`cpu`, `dram`) defines a child model that inherits from `Component`. No external dependencies (no django-polymorphic).
- **Rationale**: Each hardware component type has very distinct properties (CPU: cores, clock speed, TDP, socket; DRAM: capacity, speed, DDR type, timing). Multi-table inheritance gives each type its own database table with type-specific columns, while sharing a common base table for the general endpoint. Django handles the parent-child relationship automatically via a OneToOneField. The general endpoint queries only the base table (no JOINs), while type-specific endpoints query their child tables (auto-JOINs to base).
- **Alternatives considered**:
  - **Proxy models (single table)**: Cannot support type-specific fields. All types would share one table with many NULL columns. Rejected because CPU and DRAM have fundamentally different properties.
  - **django-polymorphic**: Adds external dependency for automatic subclass resolution on the general endpoint. Not needed because the general endpoint only needs base fields (name, type, description) — it doesn't need to return CPU-specific or DRAM-specific fields.
  - **Abstract base + union queries**: Each type is fully independent, but the general endpoint must manually merge querysets from all apps. Violates FR-009 (adding a new type requires modifying the components view). Also makes cross-type pagination/ordering complex.
  - **JSONField for type-specific data**: Keeps a single table but loses database-level constraints, indexing, and type safety on type-specific fields. Acceptable for small flexible metadata but not for core domain attributes.

## R-002: Component Type Field Design

- **Decision**: Open `CharField` (max 50 chars) on the base `Component` model with no `choices` constraint. Each child model's `save()` method auto-sets the type string (e.g., `component_type = "cpu"`).
- **Rationale**: Using Django `choices` on the model field would require modifying the `components` app and running a migration every time a new type is added. An open CharField means the `components` app never needs to change. The general endpoint can filter by type as a query parameter; unknown types simply return empty results (per edge case spec).
- **Alternatives considered**:
  - **Choices field**: Type-safe at DB level but violates FR-009 (requires model change in components for each new type)
  - **Separate ComponentType table (FK)**: Adds complexity for negligible benefit; types are simple labels
  - **Content types framework**: Over-engineered for this use case

## R-003: Container Test Strategy

- **Decision**: Use `docker compose run --rm web pytest` as the primary container test command. Add a `test` profile in docker-compose for convenience.
- **Rationale**: Reuses the existing web service image and configuration. The `--rm` flag cleans up the container after tests. Using a separate postgres instance or the existing `db` service both work since tests use Django's test database isolation. A docker-compose profile allows `docker compose --profile test run --rm test` as a single-command experience.
- **Alternatives considered**:
  - **`docker compose exec` into running container**: Requires web to be running; couples test execution to server state
  - **Separate test Dockerfile**: Duplicates build config unnecessarily
  - **Makefile/script wrapper**: Adds indirection; the docker compose command is simple enough

## R-004: Project Renaming Strategy (sample → components)

- **Decision**: Delete the entire `sample/` directory and create fresh `components/`, `cpu/`, and `dram/` apps. Do not rename/refactor in-place.
- **Rationale**: The sample app has a different data model (SampleItem). A clean replacement avoids confusing migration lineage and stale references. Test patterns from sample will be replicated in the new test files.
- **Alternatives considered**:
  - **Rename sample → components**: Preserves git history but creates confusing migration chain
  - **Keep sample alongside components**: Violates FR-008

## R-005: Test Organization for Multi-App Structure

- **Decision**: Keep tests in the top-level `tests/` directory: `tests/test_components_api.py`, `tests/test_cpu_api.py`, `tests/test_dram_api.py`. Shared fixtures in `tests/conftest.py`.
- **Rationale**: Consistent with feature 001 convention and existing pytest.ini config. Centralized fixtures (e.g., `cpu_component`, `dram_component`) are reusable across test files.
- **Alternatives considered**:
  - **Tests inside each app**: Fragments test discovery and makes cross-app fixture sharing harder
  - **Nested test directories**: Unnecessary complexity at this scale

## R-006: General Endpoint Serializer Strategy

- **Decision**: The general `/api/components/` endpoint returns base fields only (id, name, component_type, description, created_at, updated_at). It does NOT include type-specific fields. Consumers who need full detail should use the type-specific endpoint or the detail URL which includes a `component_type` field indicating which type-specific endpoint to query.
- **Rationale**: Querying the base table without JOINs keeps the general endpoint fast and simple. Including type-specific fields would require either django-polymorphic (external dependency) or manual subclass detection with per-type serialization (complex and fragile). The general endpoint serves discovery and filtering; detailed type-specific data belongs on the type endpoints.
- **Alternatives considered**:
  - **Polymorphic serializer**: Returns full type-specific fields on general endpoint. Requires django-rest-polymorphic dependency and N+1 queries to resolve subtypes.
  - **Manual subclass detection**: Check if component has a `cpucomponent` attribute, then serialize accordingly. Fragile, violates FR-009 (must update for each new type).
