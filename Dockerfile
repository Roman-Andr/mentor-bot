ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-alpine AS builder

WORKDIR /build

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
  pip install uv && \
  uv sync --no-dev --frozen --no-install-project

FROM python:${PYTHON_VERSION}-alpine

ENV AUTH_SERVICE_URL=http://auth_service:8000
ENV CHECKLISTS_SERVICE_URL=http://checklists_service:8000
ENV KNOWLEDGE_SERVICE_URL=http://knowledge_service:8000
ENV NOTIFICATION_SERVICE_URL=http://notification_service:8000
ENV ESCALATION_SERVICE_URL=http://escalation_service:8000
ENV FEEDBACK_SERVICE_URL=http://feedback_service:8000
ENV MEETING_SERVICE_URL=http://meeting_service:8000

ARG SERVICE_NAME

WORKDIR /app

RUN adduser -D appuser && apk add --no-cache su-exec tzdata

COPY --from=builder /build/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  SERVICE_NAME=${SERVICE_NAME}

COPY ${SERVICE_NAME}/${SERVICE_NAME}/ ./${SERVICE_NAME}/
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["sh", "-c", "python -m uvicorn ${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000"]

HEALTHCHECK --interval=300s --timeout=4s --start-period=20s --start-interval=3s --retries=60 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
