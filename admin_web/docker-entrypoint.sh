#!/bin/sh
set -e

if [ "$DEBUG" = "false" ]; then
  export NODE_ENV=production
  exec node server.js
else
  export NODE_ENV=development
  exec bun run dev --inspect=0.0.0.0:9229
fi
