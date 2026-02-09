# Quickstart: CPerf API

## Prerequisites

- **Docker mode**: Docker and Docker Compose installed
- **Local debug mode**: Python 3.12, VS Code with Python extension installed

## Option A: Docker Mode (Recommended for full environment)

### 1. Clone and start

```bash
git clone <repo-url> && cd cperf-api
cp .env.example .env
docker compose up --build
```

### 2. Initialize the database

In a separate terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 3. Verify

- API root: http://localhost:8000/api/
- Admin panel: http://localhost:8000/admin/
- Sample items endpoint: http://localhost:8000/api/items/

### 4. Stop

```bash
docker compose down          # Stop containers (data persists)
docker compose down -v       # Stop and remove data volumes
```

## Option B: Local F5 Debug Mode (Recommended for debugging)

### 1. Set up virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements/dev.txt
```

### 2. Initialize database (SQLite by default)

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Debug with VS Code

1. Open the project folder in VS Code
2. Press **F5** (launch configuration is pre-configured)
3. The server starts at http://localhost:8000/

Breakpoints work immediately - set them in any view, serializer, or model file.

### 4. Switch to Docker PostgreSQL (optional)

To use the Docker PostgreSQL database instead of SQLite:

1. Start only the database container:
   ```bash
   docker compose up db -d
   ```
2. Set the environment variable:
   ```bash
   # In .env.local (create if not exists)
   DATABASE_URL=postgres://cperf:cperf@localhost:5432/cperf
   ```
3. Press F5 - the app now connects to Docker PostgreSQL

## API Quick Test

```bash
# Create an item
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "A test"}'

# List all items
curl http://localhost:8000/api/items/

# Get a specific item (replace <id> with the UUID from create response)
curl http://localhost:8000/api/items/<id>/

# Update an item
curl -X PUT http://localhost:8000/api/items/<id>/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "description": "Updated"}'

# Delete an item
curl -X DELETE http://localhost:8000/api/items/<id>/
```

## Running Tests

```bash
# Docker mode
docker compose exec web pytest

# Local mode
pytest
```

## Project Structure

```
cperf-api/
├── config/                  # Django project configuration
│   ├── settings.py          # Settings (env-var driven)
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── sample/                  # Sample app (reference implementation)
│   ├── models.py            # SampleItem model
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets
│   └── urls.py              # App URL routing
├── tests/                   # Test suite
├── manage.py                # Django management script
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service orchestration
├── requirements/            # Dependency files
│   ├── base.txt             # Production dependencies
│   └── dev.txt              # Development dependencies
├── .env.example             # Environment variable template
├── .vscode/                 # VS Code configuration
│   ├── launch.json          # F5 debug configuration
│   └── settings.json        # Workspace settings
└── entrypoint.sh            # Docker entrypoint script
```
