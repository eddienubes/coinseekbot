ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-alpine as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN pip install poetry \
    && apk update \
    && apk --no-cache add \
      sudo jq git make g++ \
    && poetry config virtualenvs.in-project true
    
# Copy the source code into the container.
COPY Makefile .
COPY pyproject.toml .
COPY poetry.lock .

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    poetry install --without dev --no-interaction --no-ansi

COPY src src

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application.
CMD source .venv/bin/activate && make bot && make migrate-pg
