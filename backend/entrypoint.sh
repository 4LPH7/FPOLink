#!/bin/bash
set -e

echo "[FPOLink] Waiting for database..."
while ! python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT 1')); conn.close()"; do
    echo "[FPOLink] Database not ready, retrying in 2s..."
    sleep 2
done
echo "[FPOLink] Database is ready."

echo "[FPOLink] Running database migrations..."
alembic upgrade head

echo "[FPOLink] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
