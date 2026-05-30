FROM python:3.13-alpine AS base

# ---- system deps ----
RUN apk add --no-cache \
    build-base \
    linux-headers \
    curl

# ---- uv installation ----
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo "PATH=$PATH" && \
    ls -R /root/.cargo || true && \
    find / -name uv || true

# ---- runtime env ----
ENV UV_CACHE_DIR=/root/.cache/uv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---- copy dependency files first (for cache) ----
COPY pyproject.toml uv.lock ./

# ---- install dependencies with cache ----
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# ---- copy application code ----
COPY . .

# ---- install project itself (editable not needed in prod) ----
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---- run app ----
CMD ["uv", "run", "-m", "src"]
