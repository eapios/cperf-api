# Feature Specification: Auto-Create Superuser

**Feature Branch**: `004-auto-superuser`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "createsuperuser so we can login to /admin"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Create Admin Account on Startup (Priority: P1)

As a developer starting the application for the first time, I want a superuser account to be automatically created so that I can immediately log in to the admin panel without running a manual command.

**Why this priority**: This is the core feature — without it, developers must remember to run a separate command after every fresh database setup to access the admin panel.

**Independent Test**: Can be fully tested by starting the application with a fresh database and verifying the admin panel is accessible with the auto-created credentials.

**Acceptance Scenarios**:

1. **Given** a fresh database with no users, **When** the application starts, **Then** a superuser account is created with credentials sourced from environment configuration.
2. **Given** an existing database where the superuser already exists, **When** the application starts, **Then** no duplicate account is created and the existing account remains unchanged.
3. **Given** the required environment variables for superuser credentials are not set, **When** the application starts, **Then** superuser creation is skipped and the application starts normally.

---

### User Story 2 - Login to Admin Panel (Priority: P2)

As a developer, I want to log in to the admin panel using the auto-created superuser credentials so that I can manage data through the admin interface.

**Why this priority**: This validates that the auto-created account actually works for its intended purpose.

**Independent Test**: Can be tested by navigating to the admin login page and authenticating with the configured credentials.

**Acceptance Scenarios**:

1. **Given** the application has started and the superuser was auto-created, **When** I navigate to the admin login page and enter the configured credentials, **Then** I am granted access to the admin dashboard.

---

### Edge Cases

- What happens when the configured username already exists but is not a superuser? The system should skip creation and log a warning — it should not modify the existing account.
- What happens when the configured password is empty or blank? Superuser creation should be skipped.
- What happens when the database is unavailable at startup? The superuser creation step should fail gracefully without preventing the application from starting (existing DB-wait behavior handles this).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically create a superuser account on first startup when the required credentials are provided via environment configuration.
- **FR-002**: System MUST read the superuser username, email, and password from environment variables (not hardcoded).
- **FR-003**: System MUST skip superuser creation if the configured username already exists in the database.
- **FR-004**: System MUST skip superuser creation if the required environment variables (username and password) are not set.
- **FR-005**: System MUST log a message indicating whether the superuser was created, already existed, or was skipped due to missing configuration.

### Key Entities

- **Superuser**: An administrative user account with full access to the admin panel. Attributes: username, email, password (all sourced from environment configuration).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can access the admin panel within 30 seconds of starting the application for the first time, without running any additional commands.
- **SC-002**: 100% of application restarts with an existing superuser complete without errors or duplicate account creation.
- **SC-003**: Application starts successfully 100% of the time when superuser environment variables are absent (graceful skip).

## Assumptions

- The admin panel is already available at `/admin` (it is — Django admin is in `INSTALLED_APPS`).
- Environment variables are the standard mechanism for configuring credentials in this project (consistent with existing `DATABASE_URL`, `SECRET_KEY` pattern).
- This feature applies to both Docker and local development workflows.
- The superuser email is optional — if not provided, a reasonable default (e.g., blank or derived from username) is acceptable.
