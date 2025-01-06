FROM python:3.11.9-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    # not to ask any interactive questions
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:${PATH}"

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.in-project true

WORKDIR /app

COPY pyproject.toml poetry.lock ./

ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ] ; \
    then poetry install --no-root && yes | poetry cache clear . --all ; \
    else poetry install --no-root --only main && yes | poetry cache clear . --all ; \
    fi

FROM python:3.11.9-slim-bookworm as runtime

ENV PATH "/app/.venv/bin:/opt/app/bin:$PATH"

RUN mkdir -p \
    /opt/app/python \
    /opt/app/python/static \
    /opt/app/python/media

COPY --from=builder /app /app

WORKDIR /opt/app/python
COPY ./src .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
