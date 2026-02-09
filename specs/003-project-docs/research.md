# Research: Project Documentation Suite

**Date**: 2026-02-09 | **Branch**: `003-project-docs`

## Overview

This feature is documentation-only. No NEEDS CLARIFICATION items existed in the technical context. Research focuses on best practices for each deliverable.

## R1: README Structure Best Practices

**Decision**: Follow standard open-source README conventions with project-specific sections for dual DB mode and debugging.

**Rationale**: Developers expect a predictable README layout. The dual setup (local SQLite vs Docker PostgreSQL) is the main differentiator that needs clear separation.

**Alternatives considered**:
- Wiki-based docs → Rejected: too heavy for a small project, harder to keep in sync with code
- Sphinx/MkDocs generated site → Rejected: premature for current project size; can be added later

## R2: API Documentation Format

**Decision**: Hand-written Markdown with curl examples per endpoint, organized by resource type.

**Rationale**: The API has 3 resource endpoints (6 URL patterns total). Auto-generation (drf-spectacular/swagger) would add a dependency for minimal gain at this scale.

**Alternatives considered**:
- drf-spectacular + Swagger UI → Rejected for now: adds dependency, over-engineered for 6 endpoints. Can be revisited when endpoint count grows.
- Postman collection → Rejected: requires separate tool, not as accessible as plain Markdown

## R3: Changelog Format

**Decision**: Keep a Changelog format (keepachangelog.com) with semantic versioning.

**Rationale**: Industry standard, human-readable, and widely recognized. Version numbers (0.1.0, 0.2.0) map naturally to feature branches.

**Alternatives considered**:
- Auto-generated from git commits → Rejected: commit messages are too granular; changelog should be curated summaries
- GitHub Releases only → Rejected: not available offline, not in repo

## R4: Architecture Diagram Format

**Decision**: Mermaid diagrams embedded in Markdown.

**Rationale**: Renders natively on GitHub, stays in version control, no external tools needed. Mermaid class diagrams work well for showing model inheritance.

**Alternatives considered**:
- ASCII art → Rejected: harder to maintain, less readable for complex relationships
- Draw.io/Excalidraw images → Rejected: binary files in git, harder to diff/review

## R5: MIT License Text

**Decision**: Standard MIT License text with copyright year 2026 and project name "cperf-api".

**Rationale**: User explicitly requested MIT. Standard text from choosealicense.com.

**Alternatives considered**: None (user specified MIT).

## R6: debugpy Documentation

**Decision**: Document both VS Code launch.json and PyCharm configurations for local and Docker modes.

**Rationale**: These are the two most popular Python IDEs. debugpy is already in requirements/dev.txt. Standard attach config on port 5678.

**Alternatives considered**:
- Only VS Code → Rejected: excludes PyCharm users
- No debugger docs → Rejected: explicitly required in spec (FR-005)
