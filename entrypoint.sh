#!/bin/bash
# Container entrypoint: wait for PostgreSQL, run migrations, ensure superuser, then execute CMD

set -e

# Wait for PostgreSQL to be ready
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "postgres"; then
    DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
    DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
    echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."

    RETRIES=30
    while [ $RETRIES -gt 0 ]; do
        if pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" > /dev/null 2>&1; then
            break
        fi
        RETRIES=$((RETRIES - 1))
        echo "Waiting for PostgreSQL, ${RETRIES} remaining attempts..."
        sleep 2
    done

    if [ $RETRIES -eq 0 ]; then
        echo "ERROR: PostgreSQL did not become ready in time."
        exit 1
    fi
    echo "PostgreSQL is ready."
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser from environment variables (skips if already exists or not configured)
python manage.py ensure_superuser

# Execute the main command (CMD)
exec "$@"
