FROM python:3.13-slim AS build

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV

COPY pyproject.toml uv.lock ./
RUN uv venv $VIRTUAL_ENV
RUN uv sync --frozen --no-install-project

FROM python:3.13-slim AS dev

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY . .

CMD ["uvicorn", "image_processor.main:service", "--reload", "--host", "0.0.0.0", "--port", "8000"]