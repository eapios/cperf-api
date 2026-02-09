# Research: RESTful API Backend Initialization

**Feature Branch**: `001-drf-docker-setup`
**Date**: 2026-02-06

## R-001: Python Version

- **Decision**: Python 3.12
- **Rationale**: Latest stable Python with full Django 5.x support. Offers improved error messages, performance optimizations, and is the recommended version for new Django projects in 2026.
- **Alternatives considered**: Python 3.11 (stable but older), Python 3.13 (available but newer libraries may have compatibility gaps)

## R-002: Django & DRF Versions

- **Decision**: Django 5.1+ with Django REST Framework 3.15+
- **Rationale**: Django 5.1 is the current LTS-track release with async view support and improved form rendering. DRF 3.15 is the latest stable release with full Django 5.x compatibility.
- **Alternatives considered**: Django 4.2 LTS (still supported but lacks latest features), Django 5.0 (superseded by 5.1)

## R-003: Project Structure Pattern

- **Decision**: Single Django project with a `config` settings package and a `sample` app
- **Rationale**: Standard Django convention. The `config/` package holds settings, URLs, ASGI/WSGI configs. Each feature area gets its own Django app. Starting with one app (`sample`) keeps the structure minimal while demonstrating the pattern for future apps.
- **Alternatives considered**: Monolithic single-file settings (doesn't scale), cookiecutter-django (over-engineered for initial setup), apps within a `src/` directory (non-standard for Django)

## R-004: Dockerfile Strategy

- **Decision**: Single-stage Dockerfile using `python:3.12-slim` base image
- **Rationale**: For a development environment, multi-stage builds add complexity without meaningful benefit. The slim variant reduces image size while maintaining compatibility. Dependencies are copied and installed first for Docker layer caching.
- **Alternatives considered**: Multi-stage build (overkill for dev), Alpine-based image (musl libc causes issues with some Python packages like psycopg2), full python:3.12 image (unnecessarily large)

## R-005: Dependency Management

- **Decision**: pip with `requirements.txt` (split into base.txt and dev.txt)
- **Rationale**: Simplest approach, universally understood, works seamlessly with Docker and virtual environments. Splitting base/dev requirements keeps Docker images lean.
- **Alternatives considered**: Poetry (adds complexity to Docker builds and requires poetry installation in container), pipenv (slower, less Docker-friendly), uv (newer, fast but less mature ecosystem)

## R-006: Database Wait Strategy

- **Decision**: Custom entrypoint script that polls PostgreSQL readiness before starting Django
- **Rationale**: Using a shell script with `pg_isready` or Python-based TCP check in the entrypoint is the most reliable approach. Docker Compose `depends_on` with `condition: service_healthy` combined with a PostgreSQL healthcheck ensures the database accepts connections before Django starts.
- **Alternatives considered**: wait-for-it.sh (external dependency), Django `check --database` in a loop (works but slower), relying solely on depends_on (doesn't guarantee DB is accepting connections)

## R-007: Settings Organization for Dual Mode

- **Decision**: Single `config/settings.py` using `django-environ` to read environment variables with sensible defaults
- **Rationale**: A single settings file with environment-variable-driven configuration avoids the complexity of split settings modules. The `DATABASE_URL` pattern (or a simpler `DB_ENGINE` toggle) enables switching between SQLite and PostgreSQL with one variable. Default values ensure local debug mode works without any .env file.
- **Alternatives considered**: Split settings (base/local/docker - adds indirection for a simple project), django-configurations (third-party complexity), raw os.environ (verbose, no type casting)

## R-008: VS Code Debug Configuration

- **Decision**: launch.json with `debugpy` for Django runserver, using a dedicated `.env.local` file
- **Rationale**: VS Code's Python extension natively supports debugpy. A launch configuration targeting `manage.py runserver` with `--noreload` (debugpy handles reload) and environment variables pointing to SQLite provides zero-config F5 debugging. A `.env.local` file keeps local overrides separate from Docker's `.env`.
- **Alternatives considered**: Remote debugging into Docker container (complex, defeats the purpose of local debug), attach mode (requires manual debugpy startup), Docker dev containers (adds layer of indirection)

## R-009: Environment Variable Management

- **Decision**: `.env` file for Docker Compose, `.env.local` for local debug mode, `django-environ` in settings
- **Rationale**: Docker Compose natively loads `.env` files. A separate `.env.local` for VS Code local debug mode prevents conflicts. Both files are gitignored; `.env.example` is committed as a template. `django-environ` provides type-safe parsing with defaults.
- **Alternatives considered**: python-dotenv (manual loading, less Django-integrated), direct os.environ (no defaults, verbose), single .env for both modes (risk of Docker/local config collision)

## R-010: PostgreSQL Version

- **Decision**: PostgreSQL 16
- **Rationale**: Latest stable major version with improved performance, logical replication enhancements, and full Django 5.x compatibility. Using a specific major version tag ensures reproducibility.
- **Alternatives considered**: PostgreSQL 15 (stable but older), PostgreSQL 17 (too new for broad ecosystem support)
