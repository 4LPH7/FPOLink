#!/bin/bash
set -e

echo "[FPOLink] Waiting for database..."
while ! python -c "import psycopg; psycopg.connect('${DATABASE_URL}')" 2>/dev/null; do
    echo "[FPOLink] Database not ready, retrying in 2s..."
    sleep 2
done
echo "[FPOLink] Database is ready."

echo "[FPOLink] Running database migrations..."
alembic upgrade head

echo "[FPOLink] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
