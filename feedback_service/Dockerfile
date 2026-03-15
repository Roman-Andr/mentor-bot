FROM python:3.14-slim as builder

WORKDIR /feedback_service

# Install uv and sync dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync

FROM python:3.14-slim

WORKDIR /feedback_service

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /feedback_service/.venv /feedback_service/.venv

# Copy application code
COPY feedback_service/ ./feedback_service/

# Expose port
EXPOSE 8000

# Set PATH to include virtual environment
ENV PATH="/feedback_service/.venv/bin:$PATH"

# Run application
CMD ["uvicorn", "feedback_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
