# Stage 1: Build dependencies with uv
FROM python:3.12-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Stage 2: Runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1001 app_group && \
    useradd --system --uid 1001 --gid 1001 app_user

COPY . /app

COPY --from=builder --chown=app_user:app_group /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

USER app_user

CMD ["uvicorn", "main:app", "--log-level", "info", "--host", "0.0.0.0", "--port", "8000"]
