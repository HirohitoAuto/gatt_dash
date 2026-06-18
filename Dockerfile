# FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# RUN apt-get update && \
#     apt-get install -y sudo gcc

# WORKDIR /usr/scraping

# COPY scraping/requirements.txt .
# RUN pip install -U pip && pip install -r requirements.txt

# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/scraping`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Include development dependencies
ENV UV_NO_DEV=0

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Place executables in the environment at the front of the path
ENV PATH="/scraping/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use root user
USER root

CMD []