# userMS

User service for PersonalCook.

## Overview
UserMS provides authentication and user profile management for PersonalCook. It handles registration, login (JWT), profile access, and user lookup/search for other services.

## Architecture
- FastAPI service with PostgreSQL storage.
- JWT-based auth for protected endpoints.
- Exposes user lookup endpoints for other microservices.

## Local dev
1. docker network create personalcook-net
2. copy .env.example .env
3. docker compose up --build

## Configuration
Environment variables (see `.env.example`):
- `DATABASE_URL`: Postgres connection string.
- `JWT_SECRET`: secret used to sign tokens.
- `JWT_ALGORITHM`: JWT signing algorithm (e.g. HS256).

## Ports
- API: 8000
- Postgres: 5432

## API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Testing
Run tests locally:
```
pytest
```

## CI
This repo runs two GitHub Actions jobs:
- `test`: installs requirements and runs `pytest`.
- `container`: builds the Docker image, starts Postgres, runs the container, and hits `/` for a smoke test.

Tests (files and intent):
- `tests/test_user_routes.py`: register/login flow and user search/lookups.

## Deployment
- Docker image and Helm chart are provided for deployment.
- Health check: `GET /health`.
- Metrics: `GET /metrics` (Prometheus format).

## Troubleshooting
- `JWT_SECRET` or `JWT_ALGORITHM` missing: auth endpoints will fail.
- Database connection errors: verify `DATABASE_URL` and Postgres container status.
