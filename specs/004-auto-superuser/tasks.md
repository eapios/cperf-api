# Tasks: Auto-Create Superuser

**Input**: Design documents from `/specs/004-auto-superuser/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the management command directory structure

- [x] T001 Create management command package directories: config/management/__init__.py and config/management/commands/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Environment variable configuration that all user stories depend on

- [x] T002 [P] Add DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL to docker-compose.yml web service environment section
- [x] T003 [P] Add DJANGO_SUPERUSER_* variables to .env.example with example values

**Checkpoint**: Environment configuration ready — user story implementation can begin

---

## Phase 3: User Story 1 — Auto-Create Admin Account on Startup (Priority: P1) MVP

**Goal**: Superuser is automatically created on application startup when env vars are set

**Independent Test**: Start application with fresh DB + env vars set → superuser exists; restart → no duplicate; unset env vars → skips gracefully

### Implementation for User Story 1

- [x] T004 [US1] Implement ensure_superuser management command in config/management/commands/ensure_superuser.py — read DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL from os.environ; skip if username/password missing; check User.objects.filter(username=...).exists(); create via User.objects.create_superuser(); log outcome (created/exists/skipped)
- [x] T005 [US1] Add ensure_superuser call to entrypoint.sh after migrate and before exec "$@"

**Checkpoint**: User Story 1 complete — `docker compose up` with env vars auto-creates superuser; without env vars, starts normally

---

## Phase 4: User Story 2 — Login to Admin Panel (Priority: P2)

**Goal**: Verify the auto-created superuser can actually log in to /admin

**Independent Test**: Navigate to /admin/, enter configured credentials, verify admin dashboard access

### Implementation for User Story 2

- [x] T006 [US2] Verify Django admin is properly configured — confirm django.contrib.admin is in INSTALLED_APPS and admin URLs are registered in config/urls.py (no changes expected, just verification)

**Checkpoint**: User Stories 1 and 2 both work — superuser is created and can log in to /admin

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and cleanup

- [x] T007 [P] Update README.md — add DJANGO_SUPERUSER_* to environment section, update Docker quickstart to mention auto-superuser, remove manual createsuperuser instruction
- [x] T008 [P] Update CHANGELOG.md — add auto-superuser feature under [Unreleased]
- [x] T009 Run quickstart.md validation — follow quickstart.md steps in Docker and verify admin login works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1
- **User Story 1 (Phase 3)**: Depends on Phase 2 — core implementation
- **User Story 2 (Phase 4)**: Depends on Phase 3 — verification only
- **Polish (Phase 5)**: Depends on Phase 3

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T007 and T008 can run in parallel (different files)

---

## Parallel Example: Phase 2

```bash
# Launch foundational tasks together:
Task: "Add DJANGO_SUPERUSER_* to docker-compose.yml"
Task: "Add DJANGO_SUPERUSER_* to .env.example"
```

## Parallel Example: Phase 5

```bash
# Launch polish tasks together:
Task: "Update README.md with superuser docs"
Task: "Update CHANGELOG.md with feature entry"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002, T003)
3. Complete Phase 3: User Story 1 (T004, T005)
4. **STOP and VALIDATE**: `docker compose up` → verify superuser created → verify /admin login
5. Deploy/demo if ready

### Full Delivery

1. MVP above
2. Phase 4: Verify admin panel access (T006)
3. Phase 5: Documentation updates (T007, T008, T009)

---

## Notes

- Total tasks: 9
- Tasks per user story: US1=2, US2=1, Setup/Foundation=3, Polish=3
- Parallel opportunities: 2 groups (Phase 2: T002+T003, Phase 5: T007+T008)
- Suggested MVP: Phase 1–3 (T001–T005) — 5 tasks
- No new models, migrations, or API endpoints
