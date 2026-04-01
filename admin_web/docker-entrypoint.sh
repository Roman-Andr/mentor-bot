#!/bin/sh
set -e

mkdir -p /app/.next
chown nextjs:nodejs /app/.next 2>/dev/null || true

if [ "$DEBUG" = "false" ]; then
  export NODE_ENV=production
  exec bun run start
else
  export NODE_ENV=development
  exec bun run dev --inspect 0.0.0.0:9229
fi
