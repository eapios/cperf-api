# Research: Auto-Create Superuser

## R-001: Implementation Approach

**Decision**: Custom Django management command (`ensure_superuser`)

**Rationale**:
- Testable with Django's `call_command()` in pytest
- Follows Django conventions for startup tasks
- Idempotent by design (check-before-create)
- Can be called from both `entrypoint.sh` (Docker) and manually (local dev)

**Alternatives considered**:
- **Shell one-liner in entrypoint.sh**: Not testable with pytest, mixes Python logic into bash
- **Django signal (post_migrate)**: Runs on every `migrate` call including tests, harder to control
- **AppConfig.ready()**: Runs on every process start including management commands, causes side effects

## R-002: Environment Variable Naming

**Decision**: Use Django's built-in `DJANGO_SUPERUSER_*` convention

**Rationale**:
- Django's built-in `createsuperuser --noinput` already reads `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`
- Using the same naming convention means existing documentation and developer familiarity apply
- No custom env var parsing needed

**Variables**:
- `DJANGO_SUPERUSER_USERNAME` (required) — skip creation if absent
- `DJANGO_SUPERUSER_PASSWORD` (required) — skip creation if absent
- `DJANGO_SUPERUSER_EMAIL` (optional) — defaults to empty string

**Alternatives considered**:
- Custom names like `ADMIN_USER`/`ADMIN_PASS`: Non-standard, adds confusion

## R-003: Idempotency Strategy

**Decision**: Check if username exists via `User.objects.filter(username=...).exists()` before creating

**Rationale**:
- Simple, efficient single query
- Doesn't modify existing accounts (including non-superuser accounts with same username)
- Logs clearly what happened

**Alternatives considered**:
- `get_or_create`: Would need extra logic to set password and superuser flag correctly
- `update_or_create`: Would overwrite existing accounts — dangerous

## R-004: Where to Call the Command

**Decision**: Add to `entrypoint.sh` after `migrate`, before `exec "$@"`

**Rationale**:
- Migrations must complete before user creation (auth tables must exist)
- Consistent with existing entrypoint pattern (wait → migrate → run)
- For local dev without Docker, developers can run `python manage.py ensure_superuser` manually

**For local dev**: The command can also be called directly: `python manage.py ensure_superuser`
