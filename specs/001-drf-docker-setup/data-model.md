# Data Model: RESTful API Backend Initialization

**Feature Branch**: `001-drf-docker-setup`
**Date**: 2026-02-06

## Entities

### SampleItem

A demonstration data model used to verify the full API stack is operational.

| Field       | Type         | Constraints                          | Description                        |
| ----------- | ------------ | ------------------------------------ | ---------------------------------- |
| id          | UUID         | Primary key, auto-generated          | Unique identifier                  |
| name        | String       | Required, max 255 chars, non-blank   | Name of the sample item            |
| description | Text         | Optional, blank allowed              | Detailed description               |
| created_at  | DateTime     | Auto-set on creation, read-only      | Timestamp when record was created  |
| updated_at  | DateTime     | Auto-set on save, read-only          | Timestamp when record was modified |

**Identity & Uniqueness**: UUID primary key ensures globally unique identifiers. Name is not unique (multiple items can share a name).

**Validation Rules**:
- `name` is required and must be between 1 and 255 characters
- `description` is optional (can be null or empty string)
- `created_at` and `updated_at` are system-managed and cannot be set via API
- `id` is system-generated and cannot be set via API

**State Transitions**: None. SampleItem has no lifecycle states - it exists or it doesn't (create/delete).

## Relationships

None. SampleItem is a standalone entity with no foreign keys or associations. This is intentional - it serves as a minimal proof-of-concept.

## Indexes

| Index        | Fields     | Type    | Rationale                           |
| ------------ | ---------- | ------- | ----------------------------------- |
| PK           | id         | Primary | Default UUID primary key            |
| created_idx  | created_at | B-tree  | Support ordering by creation date   |
