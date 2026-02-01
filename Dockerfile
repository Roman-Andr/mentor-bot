FROM python:3.14-slim

WORKDIR /app

# Install dependencies
RUN pip install uv
COPY pyproject.toml .
RUN uv sync

# Copy source code
COPY mentor_bot/ ./mentor_bot/
COPY scripts/ ./scripts/

# Run the bot
CMD ["uv", "run", "-m", "mentor_bot.main"]