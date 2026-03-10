#!/bin/sh
# Generate a new Alembic migration from model changes
# Usage: ./makemigrations.sh "description of changes"

MESSAGE="${1:-auto}"
docker compose exec api uv run alembic revision --autogenerate -m "$MESSAGE"
