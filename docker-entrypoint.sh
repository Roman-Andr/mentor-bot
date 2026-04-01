#!/bin/sh
set -e

if [ -n "$STORAGE_PATH" ] && [ -d "$STORAGE_PATH" ]; then
  chown appuser:appuser "$STORAGE_PATH"
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
