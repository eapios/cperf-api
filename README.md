# cperf-api

SSD performance calculation API built with Django REST Framework. Manages hardware component specifications (NAND, CPU, DRAM), property configuration for frontend rendering, extended properties with per-instance formula values, and saved result records.

## Prerequisites

- Python 3.12+
- pip
- Git
- (Optional) Docker and Docker Compose — for PostgreSQL setup

## Environment Files

| File | Purpose | Committed? |
|------|---------|------------|
| `.env.example` | Template — lists all variables with descriptions | Yes |
| `.env` | Docker Compose secrets (`POSTGRES_*`, `SECRET_KEY`, etc.) | No (gitignored) |
| `.env.local` | Local dev overrides — loaded by Django settings instead of `.env` | No (gitignored) |

**Which file each mode reads:**

- **Local mode** — Django loads `.env.local` (preferred) or `.env`. No `DATABASE_URL` → SQLite.
- **Docker mode** — `docker-compose.yml` reads `.env` to set `POSTGRES_*` vars and constructs `DATABASE_URL`. Django inside the container reads that constructed `DATABASE_URL`.
- **Tests (local)** — same as local mode: reads `.env.local` → SQLite.
- **Tests (Docker/PostgreSQL)** — set `DATABASE_URL` in `.env.local` pointing at the running PostgreSQL container (see [Running Tests](#running-tests)).

## Quick Start (Local)

Uses SQLite — no database setup needed.

```bash
git clone <repo-url> && cd cperf-api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

Verify: http://localhost:8000/api/nand/

## Quick Start (Docker)

Uses PostgreSQL 16.

```bash
cp .env.example .env
# Edit .env — fill in POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, SECRET_KEY
docker compose up --build
```

The `entrypoint.sh` waits for PostgreSQL, runs migrations, and creates a superuser if `DJANGO_SUPERUSER_*` variables are set in `.env`.

Verify: http://localhost:8000/api/nand/

Admin panel: http://localhost:8000/admin/

## Running Tests

### Local mode (SQLite — default)

```bash
pytest
```

Django uses SQLite. No Docker required. `pytest.ini` is preconfigured (`DJANGO_SETTINGS_MODULE=config.settings`, `pythonpath=.`, `testpaths=tests`).

### Docker mode (PostgreSQL)

Run this when you want to test PostgreSQL-specific behaviour (constraints, partial unique indexes, `CheckConstraint`, etc.).

1. Start the PostgreSQL container (without the Django web service):

   ```bash
   docker compose up -d db
   ```

2. Add a `DATABASE_URL` to `.env.local` pointing at the container:

   ```ini
   # .env.local
   DATABASE_URL=postgres://<POSTGRES_USER>:<POSTGRES_PASSWORD>@localhost:5432/<POSTGRES_DB>
   ```

   Replace the placeholders with the values from your `.env`.

3. Run pytest as normal — Django picks up `DATABASE_URL` from `.env.local`:

   ```bash
   pytest
   ```

pytest-django automatically creates a `test_<POSTGRES_DB>` database, runs all tests against it, then drops it. Your dev data in `<POSTGRES_DB>` is untouched.

4. Stop the container when done:

   ```bash
   docker compose down
   ```

## Debugging

### Local (debugpy)

```bash
python -m debugpy --listen 5678 --wait-for-client manage.py runserver --noreload
```

VS Code `launch.json`:

```json
{
  "name": "Django: Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 }
}
```

### Docker debugging

Create `docker-compose.override.yml`:

```yaml
services:
  web:
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8000 --noreload
    ports:
      - "5678:5678"
```

Then `docker compose up` and attach with the same VS Code config.

## Project Structure

```
cperf-api/
├── config/              # Django settings, URLs, WSGI
├── properties/          # PropertyConfig, PropertyConfigSet, ExtendedProperty*, BaseEntity
├── nand/                # Nand, NandInstance, NandPerf
├── cpu/                 # Cpu
├── dram/                # Dram
├── results/             # ResultProfile, ResultWorkload, ResultRecord, ResultInstance
├── tests/               # pytest test suite
├── requirements/        # pip dependencies (base.txt, dev.txt)
├── docs/                # API reference, architecture docs
├── specs/               # Feature specs and implementation plans
├── Dockerfile           # Python 3.12-slim container
├── docker-compose.yml   # PostgreSQL 16 + Django
├── entrypoint.sh        # DB readiness check + migrations + superuser
├── manage.py            # Django management
└── pytest.ini           # Test configuration
```

## API Overview

| Endpoint prefix | Description |
|-----------------|-------------|
| `/api/nand/` | NAND technology definitions |
| `/api/nand-instances/` | NAND capacity/OP instances |
| `/api/nand-perf/` | NAND performance entries |
| `/api/cpu/` | CPU definitions |
| `/api/dram/` | DRAM definitions |
| `/api/property-configs/` | Column rendering configs |
| `/api/config-sets/` | Ordered config set collections |
| `/api/extended-property-sets/` | Extended property groupings |
| `/api/extended-properties/` | Extended property definitions |
| `/api/extended-property-values/` | Per-instance formula/value storage |
| `/api/result-profiles/` | Result profiles |
| `/api/result-workloads/` | Workload definitions |
| `/api/result-profile-workloads/` | Profile ↔ workload links |
| `/api/result-records/` | Saved result runs |
| `/api/result-instances/` | Per-workload result entries |

See [docs/api.md](docs/api.md) for full field reference and query parameters.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

---

Last Updated: 2026-02-24
