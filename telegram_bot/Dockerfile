FROM python:3.14-slim as builder

WORKDIR /telegram_bot

# Install uv and sync dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync

FROM python:3.14-slim

WORKDIR /telegram_bot

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /telegram_bot/.venv /telegram_bot/.venv

# Copy application code
COPY telegram_bot/ ./telegram_bot/

# Expose port
EXPOSE 8000

# Set PATH to include virtual environment
ENV PATH="/telegram_bot/.venv/bin:$PATH"

# Run application
CMD ["python", "-m", "telegram_bot.main"]