# Quickstart: Auto-Create Superuser

## Docker

1. Add superuser credentials to your `.env` file:
   ```
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_PASSWORD=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   ```

2. Start the application:
   ```bash
   docker compose up --build
   ```

3. Navigate to http://localhost:8000/admin/ and log in with the configured credentials.

## Local Development

1. Set environment variables (or add to `.env`):
   ```
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_PASSWORD=admin
   ```

2. Run the command after migrate:
   ```bash
   python manage.py migrate
   python manage.py ensure_superuser
   python manage.py runserver
   ```

3. Navigate to http://localhost:8000/admin/ and log in.

## Skipping Superuser Creation

Simply omit the `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` environment variables. The application will start normally without creating a superuser.
