# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PORT=8080
ARG COMMIT_SHA
ENV COMMIT_SHA $COMMIT_SHA
ENV PYTHONUNBUFFERED True

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

EXPOSE 8080

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["sh", "-c"]
CMD ["gunicorn -b :8080 --timeout $TIMEOUT_SECONDS podcast_generator.server.server:app --threads $MAX_INSTANCE_REQUEST_CONCURRENCY"]
