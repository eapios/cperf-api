# Data Model: Auto-Create Superuser

## Entities

### User (existing — `django.contrib.auth.models.User`)

No schema changes. This feature uses the existing Django User model.

| Field       | Type    | Notes                                    |
|-------------|---------|------------------------------------------|
| username    | string  | Sourced from `DJANGO_SUPERUSER_USERNAME` |
| email       | string  | Sourced from `DJANGO_SUPERUSER_EMAIL`    |
| password    | string  | Hashed, sourced from `DJANGO_SUPERUSER_PASSWORD` |
| is_staff    | boolean | Set to `True`                            |
| is_superuser| boolean | Set to `True`                            |

## Migrations

None required — no model changes.
