# userMS

User service for PersonalCook.

## Local dev
1. docker network create personalcook-net
2. copy .env.example .env
3. docker compose up --build

## Ports
- API: 8000
- Postgres: 5432

## API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## CI
This repo runs two GitHub Actions jobs:
- test: installs requirements and runs `pytest`
- container: builds the Docker image, starts Postgres, runs the container, and hits `/` for a smoke test

Tests (files and intent):
- `tests/test_user_routes.py`: register/login flow and user search/lookups.
