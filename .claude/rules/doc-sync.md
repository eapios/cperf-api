# Documentation Sync

After any code change, update affected docs before committing:

- **Models/serializers/views/urls** → `docs/api.md`, `docs/architecture.md`
- **Docker/infra files** → `README.md` Docker section
- **Dependencies** → `README.md` prerequisites
- **Settings/env vars** → `README.md`, `docs/architecture.md`
- **Any feature/fix** → `CHANGELOG.md` under `[Unreleased]`

Bump `Last Updated: YYYY-MM-DD` in each modified doc.
