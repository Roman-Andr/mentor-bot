FROM python:3.14-slim as builder

WORKDIR /auth_service

# Install uv and sync dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync

FROM python:3.14-slim

WORKDIR /auth_service

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /auth_service/.venv /auth_service/.venv

# Copy application code
COPY auth_service/ ./auth_service/

# Expose port
EXPOSE 8000

# Set PATH to include virtual environment
ENV PATH="/auth_service/.venv/bin:$PATH"

# Run application
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]