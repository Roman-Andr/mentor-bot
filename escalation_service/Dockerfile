FROM python:3.14-slim as builder

WORKDIR /escalation_service

# Install uv and sync dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync

FROM python:3.14-slim

WORKDIR /escalation_service

# Install system dependencies (если нужен curl для health checks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /escalation_service/.venv /escalation_service/.venv

# Copy application code
COPY escalation_service/ ./escalation_service/

# Expose port
EXPOSE 8000

# Set PATH to include virtual environment
ENV PATH="/escalation_service/.venv/bin:$PATH"

# Run application
CMD ["uvicorn", "escalation_service.main:app", "--host", "0.0.0.0", "--port", "8000"]