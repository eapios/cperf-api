# Feature Specification: Hardware Component API & Project Restructure

**Feature Branch**: `002-hardware-component-api`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "1. Add and run test for container mode, 2. this project will have to provide multiple hardware component (CPU/DRAM/etc.) information, please modify the project structure to meet this requirement, 3. that means you should not name your project code folder 'sample', this project name is cperf_api so you may name it like that (or you what do you suggest follow drf convention?)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Components Across All Types (Priority: P1)

An API consumer queries hardware components across all types through a unified endpoint. They can list all components regardless of type, filter by type, search by name, and retrieve any individual component by its identifier. This provides a single entry point for discovering and browsing all hardware data in the system.

**Why this priority**: This is the foundational read path. A unified query endpoint lets consumers explore all hardware data without needing to know which type-specific endpoint to call.

**Independent Test**: Can be fully tested by creating components of different types and verifying the general endpoint returns, filters, and paginates them correctly.

**Acceptance Scenarios**:

1. **Given** components of types CPU and DRAM exist, **When** a consumer requests the general components list, **Then** the system returns a paginated list containing both CPU and DRAM entries.
2. **Given** components of type "CPU" exist, **When** a consumer requests components filtered by type "CPU", **Then** only CPU components are returned.
3. **Given** a specific component exists, **When** a consumer requests that component by its identifier via the general endpoint, **Then** the system returns the full component details.
4. **Given** no components exist, **When** a consumer requests the general list, **Then** the system returns an empty list with a successful status.

---

### User Story 2 - Manage Components via Type-Specific Endpoints (Priority: P2)

An API consumer accesses dedicated endpoints for each hardware component type (e.g., a CPU endpoint, a DRAM endpoint). Each type-specific endpoint provides full CRUD operations scoped to that component type. This allows consumers to work with type-aware validation, type-specific fields, and clean URL semantics (e.g., `/api/cpu/`, `/api/dram/`).

**Why this priority**: Type-specific endpoints are where the real domain value lives — each component type can evolve its own fields, validation rules, and behavior independently. However, they build on the shared data foundation from P1.

**Independent Test**: Can be fully tested by performing create, read, update, and delete operations on each type-specific endpoint and verifying data isolation and validation per type.

**Acceptance Scenarios**:

1. **Given** the CPU endpoint exists, **When** a consumer creates a CPU component with valid data, **Then** the system creates it and the component appears in both the CPU endpoint and the general components endpoint.
2. **Given** a DRAM component exists, **When** a consumer updates it via the DRAM endpoint, **Then** the changes are persisted and reflected in both the DRAM and general endpoints.
3. **Given** a CPU component exists, **When** a consumer deletes it via the CPU endpoint, **Then** it is removed from both the CPU and general endpoints.
4. **Given** invalid data (e.g., missing name), **When** a consumer submits it to any type-specific endpoint, **Then** the system rejects the request with clear validation errors.

---

### User Story 3 - Run Tests in Container Environment (Priority: P3)

A developer runs the project's automated test suite inside the containerized environment to verify that the application behaves correctly in the same environment it will be deployed in. This catches environment-specific issues (missing dependencies, configuration differences) before deployment.

**Why this priority**: Container testing validates deployment readiness. It builds on top of the existing local test suite (P1/P2) by ensuring those same tests pass within the container, so it depends on having working tests first.

**Independent Test**: Can be fully tested by running a single command that executes the test suite inside the container and reports pass/fail results.

**Acceptance Scenarios**:

1. **Given** the project containers are buildable, **When** a developer runs the container test command, **Then** the full test suite executes inside the container and reports results to the terminal.
2. **Given** all tests pass locally, **When** a developer runs them in container mode, **Then** the same tests pass in the container environment.
3. **Given** a test failure occurs in the container, **When** the test suite completes, **Then** the failure details are clearly reported with the same level of detail as local test runs.

---

### Edge Cases

- What happens when a component type is requested that does not exist in the system? The general endpoint returns an empty list (not an error).
- What happens when creating a component with a duplicate name within the same type? The system allows it (components are distinguished by unique identifiers).
- What happens when the container test database is unavailable? The test suite fails fast with a clear connection error rather than hanging.
- What happens when a consumer accesses a type-specific endpoint that has no entries? The endpoint returns an empty list with a successful status.
- What happens when a consumer creates a component via a type-specific endpoint? The component automatically appears in the general components query with the correct type.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST organize the codebase with a `components` Django application package that replaces the current "sample" placeholder, following the DRF domain-convention. This app hosts the shared base model and general query endpoint.
- **FR-002**: The system MUST provide type-specific Django apps (starting with `cpu` and `dram`) that each offer dedicated CRUD endpoints scoped to that component type.
- **FR-003**: The system MUST provide a general components endpoint that lists and retrieves components across all types, with filtering by type, search, pagination, and ordering.
- **FR-004**: Components created via a type-specific endpoint MUST be accessible through the general components endpoint, and vice versa.
- **FR-005**: The system MUST validate that required fields (name) are present and non-empty when creating or updating components on any endpoint.
- **FR-006**: The system MUST support running the full automated test suite inside the container environment with a single command.
- **FR-007**: The system MUST retain pagination, ordering, and search capabilities from the existing infrastructure when serving component data.
- **FR-008**: The system MUST cleanly migrate away from the "sample" application, removing all sample-specific code and replacing it with the new component structure.
- **FR-009**: Adding a new component type MUST follow a well-defined, repeatable pattern: create a new type-specific app, register its endpoints, and it automatically appears in the general components query.

### Key Entities

- **Hardware Component**: Base entity shared across all types. Key attributes: unique identifier, name, component type, description, and timestamps (created, updated). Serves as the common data shape for the general components endpoint.
- **CPU Component**: A hardware component of type CPU. Inherits base attributes and may include CPU-specific fields (to be defined as the domain grows).
- **DRAM Component**: A hardware component of type DRAM. Inherits base attributes and may include DRAM-specific fields (to be defined as the domain grows).
- **Component Type**: A categorization label (CPU, DRAM, etc.) used for filtering in the general endpoint and for routing to type-specific endpoints.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All existing test scenarios continue to pass after the project restructure (zero regressions).
- **SC-002**: The automated test suite runs successfully inside the container environment and produces the same pass/fail results as local execution.
- **SC-003**: API consumers can retrieve hardware component data filtered by type, with results returned in under 1 second for collections of up to 1,000 components.
- **SC-004**: Adding a new component type follows a repeatable pattern that requires only creating a new type-specific app and registering it — no changes to the general components query logic.
- **SC-005**: The project folder structure uses clear, convention-following names with no remnants of the "sample" placeholder.
- **SC-006**: Components created via type-specific endpoints are immediately queryable through the general components endpoint.

## Clarifications

### Session 2026-02-09

- Q: Should the app be named `components` (DRF domain-convention) or `cperf` (project-centric)? → A: `components` — follows DRF convention of naming apps by their domain.
- Q: Should the system use a single generic app or separate per-type endpoints? → A: Both — a `components` app for general cross-type queries, plus separate apps per component type (`cpu`, `dram`) with their own CRUD endpoints.

## Assumptions

- The existing Docker and docker-compose infrastructure from feature 001 is in place and working.
- Type-specific apps (e.g., `cpu`, `dram`) share a common base model from `components` to enable the general query endpoint.
- Type-specific apps start with the same base fields as the shared model; type-specific fields can be added incrementally as domain requirements emerge.
- Container test mode uses the same database backend (PostgreSQL) as the production container, not SQLite.
- The "sample" app and all its artifacts (model, views, serializers, tests, migrations, URLs) will be fully replaced, not retained alongside the new structure.
