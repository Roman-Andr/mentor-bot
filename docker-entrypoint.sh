#!/bin/sh
set -e

if [ -n "$STORAGE_PATH" ] && [ -d "$STORAGE_PATH" ]; then
  chown appuser:appuser "$STORAGE_PATH"
fi

# Run Alembic migrations before starting (no-op when versions/ is empty).
# On first deploy against a DB that was already created by init_db (no
# alembic_version row), stamp to head so existing tables are not re-created.
if [ -f "/app/alembic.ini" ] && [ "$SERVICE_NAME" != "telegram_bot" ]; then
  if gosu appuser /app/.venv/bin/python -m alembic upgrade head; then
    timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
    echo "${timestamp} | INFO     | alembic:entrypoint:0 - Migrations applied."
  else
    timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
    echo "${timestamp} | WARNING  | alembic:entrypoint:0 - alembic upgrade failed, stamping head (baseline for existing schema)"
    gosu appuser /app/.venv/bin/python -m alembic stamp head
  fi
fi

if [ "$DEBUG" = "true" ]; then
  if [ "$SERVICE_NAME" = "telegram_bot" ]; then
    exec gosu appuser python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5671 -m telegram_bot.main
  else
    exec gosu appuser python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5671 -m uvicorn ${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000
  fi
else
  if [ "$SERVICE_NAME" = "telegram_bot" ]; then
    exec gosu appuser python -m telegram_bot.main
  else
    exec gosu appuser "$@"
  fi
fi
