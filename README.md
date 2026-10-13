# Service Management REST API

[![Python CI](https://github.com/MGCrewLokote/service-management-api/actions/workflows/ci.yml/badge.svg)](https://github.com/MGCrewLokote/service-management-api/actions/workflows/ci.yml)

A practical, testable **Python backend engineering portfolio project**: a REST API for tracking IT service tickets. Built with FastAPI, SQLAlchemy, PostgreSQL, Alembic, Docker, and pytest.

> **Scope:** This is an educational MVP built with synthetic data. It is not a commercial help desk product or a production-ready identity system.

## Features

- Create, list, inspect, update, and delete service tickets.
- Ticket fields: title, description, status, priority, assignee, and timestamps.
- Query filtering by status, priority, and assignee, plus sorting and pagination.
- Simple bearer-token protection for ticket endpoints.
- PostgreSQL persistence and an Alembic schema migration.
- Interactive OpenAPI docs and automated API tests.
- Docker Compose for local development and GitHub Actions CI.

## Tech stack

Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2, PostgreSQL 16, Alembic, pytest, Docker and Ruff.

## Quick start with Docker

1. Install Docker with Docker Compose.
2. Clone this repository.
3. Copy `.env.example` to `.env`.
4. Replace the example values with your own local-only token and database password.
5. Start the services:

```bash
docker compose up --build
```

The database schema is migrated automatically at container startup.

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The API is bound to localhost by default so it is not directly exposed to your network.

## Example requests

Set your own token from `.env` in the request's Authorization header:

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Authorization: Bearer YOUR_LOCAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Email delivery failed","description":"SMTP timeout","priority":"high","assigned_to":"alex"}'

curl -H "Authorization: Bearer YOUR_LOCAL_TOKEN" \
  "http://localhost:8000/tickets?priority=high&sort=newest&limit=10"
```

Valid statuses: `open`, `in_progress`, `resolved`, `closed`.
Valid priorities: `low`, `medium`, `high`, `critical`.

## Run tests

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
```

Tests use an isolated in-memory SQLite database; the Docker application uses PostgreSQL. To run the API locally without Docker, set `DATABASE_URL` and `APP_API_TOKEN`, then run `alembic upgrade head` and `uvicorn app.main:app --reload`.

## Project structure

```text
app/                  FastAPI routes, models, schemas, DB and authentication
alembic/              Versioned SQL schema migration
tests/                Isolated API tests
.github/workflows/     Continuous integration
Dockerfile            Application image
docker-compose.yml    Local PostgreSQL and API services
pyproject.toml        Dependencies and tooling
```

## Architecture decisions and limitations

- **Layering:** API schemas are separate from SQLAlchemy persistence models; request-scoped sessions provide predictable database lifecycle.
- **Migrations:** Schema changes use Alembic instead of creating tables at runtime.
- **Security:** A single environment-configured bearer token is appropriate for this local portfolio demonstration only; it does **not** provide user identities, RBAC, token rotation or production-grade authentication.
- **Testing:** The API behavior is tested using SQLite for speed; PostgreSQL integration testing is a logical next step.
- **Observability:** The health endpoint is a liveness check; metrics, tracing, and production monitoring are not yet implemented.
- **Deployment:** Docker Compose is configured for local evaluation, not internet-facing production.

## Next iterations

1. Users, JWT-based authentication, role permissions and audit history.
2. Search, stronger domain validation and database integration tests.
3. Structured logs, request IDs, tracing and rate limiting.
4. Production deployment configuration and security hardening.

## License

MIT. See [LICENSE](LICENSE).

Created as part of [Amaury Molina's engineering portfolio](https://github.com/MGCrewLokote).
