FROM oven/bun:alpine AS deps

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# ── Development stage ─────────────────────────────────────────────────────────
# Source copied directly here — not from builder — so frequent code changes
# don't invalidate the deps layer. In practice the whole dir is bind-mounted.
FROM oven/bun:alpine AS dev

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1 \
  PORT=3000 \
  HOSTNAME="0.0.0.0"

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN chmod +x ./docker-entrypoint.sh

EXPOSE 3000 9229

ENTRYPOINT ["./docker-entrypoint.sh"]

# ── Production build ──────────────────────────────────────────────────────────
# Build output + entrypoint staged under /build/runner so the runner stage
# needs only a single COPY --from=builder.
FROM oven/bun:alpine AS builder

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN bun run build && \
  mkdir -p /build/runner/.next && \
  cp -r .next/standalone/. /build/runner/ && \
  cp -r .next/static        /build/runner/.next/static && \
  cp -r public              /build/runner/public && \
  mkdir -p /build/runner/scripts && \
  cp scripts/log-wrap.mjs   /build/runner/scripts/log-wrap.mjs && \
  cp docker-entrypoint.sh   /build/runner/docker-entrypoint.sh && \
  chmod +x /build/runner/docker-entrypoint.sh

# ── Production runner ─────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1 \
  NODE_ENV=production \
  PORT=3000 \
  HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
  adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /build/runner/ ./

USER nextjs

EXPOSE 3000

ENTRYPOINT ["./docker-entrypoint.sh"]
