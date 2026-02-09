# cperf-api

Hardware component performance API built with Django REST Framework. Provides REST endpoints for managing and querying hardware component specifications including CPUs and DRAM modules.

## Prerequisites

- Python 3.12+
- pip
- Git
- (Optional) Docker and Docker Compose — for PostgreSQL setup

## Quick Start (Local)

```bash
git clone <repo-url> && cd cperf-api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver
```

Local mode uses SQLite by default (no `DATABASE_URL` needed).

Verify: http://localhost:8000/api/components/

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Docker mode uses PostgreSQL 16. The `entrypoint.sh` waits for PostgreSQL and auto-runs migrations.

Verify: http://localhost:8000/api/components/

Create superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

## Running Tests

```bash
pytest
```

`pytest.ini` is preconfigured (`DJANGO_SETTINGS_MODULE=config.settings`, `pythonpath=.`, `testpaths=tests`). Tests run against SQLite by default.

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

PyCharm: Run > Edit Configurations > Python Debug Server > host=localhost, port=5678

### Docker debugging

Create `docker-compose.override.yml`:

```yaml
services:
  web:
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8000 --noreload
    ports:
      - "5678:5678"
```

Then `docker compose up` and attach with the same VS Code/PyCharm config.

## Project Structure

```
cperf-api/
├── config/              # Django settings, URLs, WSGI
├── components/          # Base component model (read-only API)
├── cpu/                 # CPU component (full CRUD)
├── dram/                # DRAM component (full CRUD)
├── tests/               # pytest test suite
├── requirements/        # pip dependencies (base.txt, dev.txt)
├── docs/                # API reference, architecture docs
├── Dockerfile           # Python 3.12-slim container
├── docker-compose.yml   # PostgreSQL 16 + Django
├── entrypoint.sh        # DB readiness check + migrations
├── manage.py            # Django management
└── pytest.ini           # Test configuration
```

## API Overview

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/components/` | GET | List/retrieve all components (read-only) |
| `/api/cpu/` | GET, POST, PUT, PATCH, DELETE | CPU component CRUD |
| `/api/dram/` | GET, POST, PUT, PATCH, DELETE | DRAM component CRUD |

See [docs/api.md](docs/api.md) for full API reference.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

---

Last Updated: 2026-02-09
