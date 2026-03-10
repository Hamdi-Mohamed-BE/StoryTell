#!/bin/sh
# Apply all pending Alembic migrations
docker compose exec api uv run alembic upgrade head
