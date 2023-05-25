FROM python:3.11

ARG environment=localhost
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV VENV_PATH="/app/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN mkdir -p /app/run /app/log

RUN apt update && apt install -y libpq5 && rm -rf /var/lib/apt/lists/*
RUN pip install -U pip setuptools

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY pyproject.toml poetry.lock README.md ./
COPY coex_translator ./coex_translator

RUN poetry config virtualenvs.create false
RUN poetry install --with dev

RUN useradd --no-create-home -s /bin/bash  peasant
RUN chown -R peasant:peasant /app

USER peasant

EXPOSE 8000
