# Quickstart: CPerf API (Feature 002)

## Prerequisites

- **Docker mode**: Docker and Docker Compose installed
- **Local debug mode**: Python 3.12, VS Code with Python extension

## Running the Project (Container Mode)

### Start

```bash
cp .env.example .env
docker compose up --build
```

The entrypoint script automatically waits for PostgreSQL and runs migrations.

### Verify

- General components: http://localhost:8000/api/components/
- CPU components: http://localhost:8000/api/cpu/
- DRAM components: http://localhost:8000/api/dram/
- Admin panel: http://localhost:8000/admin/

### Stop

```bash
docker compose down          # Stop containers (data persists)
docker compose down -v       # Stop and remove data volumes
```

## Debugging the Project

### VS Code F5 Debug (Local Mode)

1. Set up virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   pip install -r requirements/dev.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Press **F5** in VS Code — the launch configuration is pre-configured in `.vscode/launch.json`.

Breakpoints work in any view, serializer, or model file. The debug config uses `--noreload` (debugpy handles the process).

### Debug with Docker PostgreSQL

To debug locally but use the Docker PostgreSQL database:

1. Start only the database: `docker compose up db -d`
2. Create/edit `.env.local`:
   ```
   DATABASE_URL=postgres://cperf:cperf@localhost:5432/cperf
   ```
3. Press F5 — the app connects to Docker PostgreSQL instead of SQLite.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable            | Default                             | Description                    |
|---------------------|-------------------------------------|--------------------------------|
| `SECRET_KEY`        | `django-insecure-dev-only-...`      | Django secret key              |
| `DEBUG`             | `True`                              | Debug mode                     |
| `ALLOWED_HOSTS`     | `localhost,127.0.0.1`               | Allowed host headers           |
| `DATABASE_URL`      | `sqlite:///db.sqlite3`              | Database connection URL        |
| `POSTGRES_DB`       | `cperf`                             | PostgreSQL database name       |
| `POSTGRES_USER`     | `cperf`                             | PostgreSQL user                |
| `POSTGRES_PASSWORD` | `cperf`                             | PostgreSQL password            |
| `APP_PORT`          | `8000`                              | Host port mapping              |

**Config files**:
- `.env` — Docker Compose environment (gitignored)
- `.env.local` — VS Code local debug overrides (gitignored)
- `.env.example` — Template with defaults (committed)

## Database Migrations

### When to run migrations

- After pulling new code that includes model changes
- After creating or modifying model fields
- **Container mode**: Migrations run automatically on startup (via `entrypoint.sh`)
- **Local mode**: Run manually after model changes

### Migration commands

```bash
# Local mode
python manage.py makemigrations              # Generate migration files
python manage.py migrate                     # Apply migrations

# Container mode (manual)
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Container mode (automatic)
# Migrations are applied automatically when the container starts
```

### Creating migrations for a new component type

When adding a new component type app (e.g., `gpu`):

```bash
python manage.py makemigrations gpu          # Generate migration for the new app
python manage.py migrate gpu                 # Apply it
```

## Running Tests

### Local mode

```bash
pytest                                       # Run all tests
pytest tests/test_cpu_api.py                 # Run CPU tests only
pytest -v                                    # Verbose output
pytest --cov=components --cov=cpu --cov=dram # With coverage
```

### Container mode

```bash
docker compose run --rm web pytest           # Run tests in container
docker compose run --rm web pytest -v        # Verbose
```

Container tests use the PostgreSQL database (same as production), ensuring environment parity.

## API Quick Test

```bash
# Create a CPU component
curl -X POST http://localhost:8000/api/cpu/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Intel Core i9-14900K", "cores": 24, "threads": 32, "clock_speed": "3.20", "boost_clock": "6.00", "tdp": 253, "socket": "LGA1700"}'

# Create a DRAM component
curl -X POST http://localhost:8000/api/dram/ \
  -H "Content-Type: application/json" \
  -d '{"name": "G.Skill Trident Z5 RGB", "capacity_gb": 32, "speed_mhz": 6000, "ddr_type": "DDR5", "modules": 2, "cas_latency": 30}'

# List all components (both types)
curl http://localhost:8000/api/components/

# Filter by type
curl "http://localhost:8000/api/components/?component_type=cpu"

# Get CPU details
curl http://localhost:8000/api/cpu/{id}/
```

## Project Structure

```
cperf-api/
├── config/                  # Django project configuration
│   ├── settings.py          # Settings (env-var driven)
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── components/              # Base component app (general endpoint)
│   ├── models.py            # Component base model
│   ├── serializers.py       # Base serializer
│   ├── views.py             # General components ViewSet (read-only)
│   └── urls.py              # /api/components/ routing
├── cpu/                     # CPU component app
│   ├── models.py            # CpuComponent model (inherits Component)
│   ├── serializers.py       # CPU-specific serializer
│   ├── views.py             # CPU CRUD ViewSet
│   └── urls.py              # /api/cpu/ routing
├── dram/                    # DRAM component app
│   ├── models.py            # DramComponent model (inherits Component)
│   ├── serializers.py       # DRAM-specific serializer
│   ├── views.py             # DRAM CRUD ViewSet
│   └── urls.py              # /api/dram/ routing
├── tests/                   # Test suite
│   ├── conftest.py          # Shared fixtures
│   ├── test_components_api.py
│   ├── test_cpu_api.py
│   └── test_dram_api.py
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── requirements/
    ├── base.txt
    └── dev.txt
```
