#!/bin/sh
set -e
if [ -n "$STORAGE_PATH" ] && [ -d "$STORAGE_PATH" ]; then
  chown appuser:appuser "$STORAGE_PATH"
fi
exec su-exec appuser "$@"
