# Kanban Manager API Architecture

This document captures the high-level design for the Kanban Manager API.

## High-Level Overview
- **Framework**: Django 5 + Django REST Framework with SimpleJWT for auth and drf-spectacular for schema generation.
- **Data Stores**: PostgreSQL 16 for relational data and Redis for caching plus Celery broker/result backend.
- **Async Processing**: Celery worker + beat for notifications, background jobs, and recurring maintenance tasks.
- **Deployment Targets**: Dockerized micro-services orchestrated by docker-compose (web, worker, beat, nginx, db, redis).

## App Responsibilities
| App | Responsibility |
| --- | -------------- |
| `users` | Custom user model, JWT auth endpoints, profile settings |
| `teams` | Team CRUD, membership, role-based access |
| `projects` | Projects inside teams, membership bridging |
| `boards` | Kanban boards per project, sharing permissions |
| `lists` | Canonical workflow stages, drag & drop order management |
| `tasks` | Core work items, tagging, attachments, subtasks |
| `comments` | Task discussion threads and mentions |
| `activity` | Event logging via signals for auditing |
| `notifications` | Delivery of async events via Celery + Redis |

## Cross-Cutting Modules
- `core.middleware` for correlation IDs and request timing.
- `core.permissions` for reusable DRF permission classes (team/project/task scoping).
- `core.utils` for helpers: ordering mixins, queryset filters, pagination, filtering utilities.

## API Surface
- Versioned API paths mounted at `/api/v1/` using DRF routers per app.
- JWT endpoints under `/api/v1/auth/`.
- Schema + Swagger UI from drf-spectacular at `/api/schema/` and `/api/docs/`.

## Data Flow Highlights
1. **Authentication** via JWT; tokens issued after login/registration.
2. **Permissions** cascade: User → Team membership → Project access → Board/List/Task visibility.
3. **Signals** emit activity entries and queue notification jobs.
4. **Celery** handles notification dispatch, digest emails, overdue reminders.

## Deployment Flow
1. `docker-compose up --build` starts db, redis, web, worker, beat, nginx.
2. `entrypoint.sh` runs migrations, collects static assets, and launches Gunicorn.
3. Nginx proxies HTTPS/TLS termination (certificate mounting optional) to Gunicorn.

This plan underpins the implementation that follows.
