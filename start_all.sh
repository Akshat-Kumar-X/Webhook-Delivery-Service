#!/usr/bin/env bash
set -e  # exit on first failure

PORT="${PORT:-8000}"  # fallback to port 8000 if not provided

echo "🔄 Running Alembic migrations..."
poetry run alembic upgrade head

echo "🚀 Starting FastAPI (Uvicorn) on port $PORT ..."
poetry run uvicorn src.app.main:app --host 0.0.0.0 --port "$PORT" &
UVICORN_PID=$!

echo "⚙️  Starting Celery worker + beat ..."
# -B embeds beat scheduler in the worker process
exec poetry run celery -A app.celery_app.celery worker -B \
     -Q deliver --loglevel=info --concurrency=4
