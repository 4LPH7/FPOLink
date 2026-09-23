#!/bin/bash
set -e

echo "[FPOLink Production] Waiting for database..."
while ! python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT 1')); conn.close()" 2>/dev/null; do
    echo "[FPOLink Production] Database not ready, retrying in 2s..."
    sleep 2
done
echo "[FPOLink Production] Database is ready."

echo "[FPOLink Production] Running database migrations..."
alembic upgrade head

echo "[FPOLink Production] Starting API server (production mode, 2 workers)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
