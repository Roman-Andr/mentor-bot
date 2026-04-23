#!/bin/sh
set -e

if [ -n "$STORAGE_PATH" ] && [ -d "$STORAGE_PATH" ]; then
  chown appuser:appuser "$STORAGE_PATH"
fi

# Run Alembic migrations before starting (no-op when versions/ is empty).
# On first deploy against a DB that was already created by init_db (no
# alembic_version row), stamp to head so existing tables are not re-created.
if [ -f "/app/alembic.ini" ] && [ "$SERVICE_NAME" != "telegram_bot" ]; then
  if su-exec appuser alembic upgrade head; then
    echo "Migrations applied."
  else
    echo "alembic upgrade failed, stamping head (baseline for existing schema)"
    su-exec appuser alembic stamp head
  fi
fi

if [ "$DEBUG" = "true" ]; then
  if [ "$SERVICE_NAME" = "telegram_bot" ]; then
    exec su-exec appuser python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5671 -m telegram_bot.main
  else
    exec su-exec appuser python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5671 -m uvicorn ${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000
  fi
else
  if [ "$SERVICE_NAME" = "telegram_bot" ]; then
    exec su-exec appuser python -m telegram_bot.main
  else
    exec su-exec appuser "$@"
  fi
fi
