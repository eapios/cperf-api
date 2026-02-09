# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Last Updated: 2026-02-09

## [Unreleased]

### Added

- Project documentation: README.md, API reference, architecture docs, changelog
- MIT License

## [0.2.0] - 2026-02-09

### Added

- Hardware component API with Component base model (UUID primary key, name, component_type, description, timestamps)
- CPU component endpoint (`/api/cpu/`) with full CRUD operations
  - Fields: cores, threads, clock_speed, boost_clock, tdp, socket
  - Validation: threads >= cores, boost_clock >= clock_speed
- DRAM component endpoint (`/api/dram/`) with full CRUD operations
  - Fields: capacity_gb, speed_mhz, ddr_type, modules, cas_latency, voltage
- Read-only general components endpoint (`/api/components/`) with filtering, search, and ordering
- Cross-endpoint visibility: components created via type-specific endpoints appear in the general listing
- Multi-table inheritance pattern: CpuComponent and DramComponent extend Component base model
- django-filter integration for component_type filtering

## [0.1.0] - 2026-02-06

### Added

- Django 5.1 project scaffolding with Django REST Framework 3.15
- Docker Compose setup with PostgreSQL 16 and Django development server
- Dual database support: SQLite for local development, PostgreSQL for Docker
- Container entrypoint with PostgreSQL readiness check and auto-migration
- debugpy integration for remote debugging
- pytest and pytest-django test configuration
- Environment management with django-environ and .env files
- Code style configuration: black, isort, flake8
