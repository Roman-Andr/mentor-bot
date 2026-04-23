ARG PYTHON_VERSION=3.14

# ── Dependencies ──────────────────────────────────────────────────────────────
# Installs Python deps into a venv. Reused by dev and prod, so service code
# changes never invalidate this layer.
FROM python:${PYTHON_VERSION}-alpine AS deps

ARG SERVICE_NAME

WORKDIR /build

COPY ${SERVICE_NAME}/pyproject.toml ${SERVICE_NAME}/uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
  pip install uv && \
  uv sync --no-dev --frozen --no-install-project

# ── Runtime base (shared by dev + prod) ───────────────────────────────────────
FROM python:${PYTHON_VERSION}-alpine AS base

ARG SERVICE_NAME

ENV AUTH_SERVICE_URL=http://auth_service:8000 \
  CHECKLISTS_SERVICE_URL=http://checklists_service:8000 \
  KNOWLEDGE_SERVICE_URL=http://knowledge_service:8000 \
  NOTIFICATION_SERVICE_URL=http://notification_service:8000 \
  ESCALATION_SERVICE_URL=http://escalation_service:8000 \
  FEEDBACK_SERVICE_URL=http://feedback_service:8000 \
  MEETING_SERVICE_URL=http://meeting_service:8000 \
  PATH="/app/.venv/bin:$PATH" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  SERVICE_NAME=${SERVICE_NAME}

WORKDIR /app

RUN adduser -D appuser && apk add --no-cache su-exec tzdata

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["sh", "-c", "python -m uvicorn ${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000"]

HEALTHCHECK --interval=15s --timeout=4s --start-period=30s --start-interval=2s --retries=10 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

# ── Development ───────────────────────────────────────────────────────────────
# Service code is bind-mounted from docker-compose.yml — deliberately NOT
# copied here so editing a .py file never invalidates an image layer.
# The [i] / [s] brackets make alembic.ini and migrations/ optional: services
# without them (e.g. telegram_bot) skip the copy instead of failing.
FROM base AS dev

ARG SERVICE_NAME

COPY --from=deps /build/.venv /app/.venv
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY ${SERVICE_NAME}/alembic.in[i] /app/alembic.ini
COPY ${SERVICE_NAME}/migration[s]/ /app/migrations/
RUN chmod +x /app/docker-entrypoint.sh

# ── Builder (prod staging) ────────────────────────────────────────────────────
# Collects venv + code + migrations + entrypoint under /build/app so the prod
# stage needs a single COPY --from=builder and stays flat.
FROM python:${PYTHON_VERSION}-alpine AS builder

ARG SERVICE_NAME

COPY --from=deps /build/.venv /build/app/.venv
COPY ${SERVICE_NAME}/${SERVICE_NAME}/ /build/app/${SERVICE_NAME}/
COPY docker-entrypoint.sh /build/app/docker-entrypoint.sh
COPY ${SERVICE_NAME}/alembic.in[i] /build/app/alembic.ini
COPY ${SERVICE_NAME}/migration[s]/ /build/app/migrations/
RUN chmod +x /build/app/docker-entrypoint.sh

# ── Production ────────────────────────────────────────────────────────────────
FROM base AS prod

COPY --from=builder /build/app/ /app/
