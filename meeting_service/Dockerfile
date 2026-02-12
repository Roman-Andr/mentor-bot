FROM python:3.14-slim as builder

WORKDIR /meeting_service

# Install uv and sync dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync

FROM python:3.14-slim

WORKDIR /meeting_service

# Install system dependencies (если нужен curl для health checks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /meeting_service/.venv /meeting_service/.venv

# Copy application code
COPY meeting_service/ ./meeting_service/

# Expose port
EXPOSE 8000

# Set PATH to include virtual environment
ENV PATH="/meeting_service/.venv/bin:$PATH"

# Run application
CMD ["uvicorn", "meeting_service.main:app", "--host", "0.0.0.0", "--port", "8000"]