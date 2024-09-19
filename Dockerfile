FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

RUN mkdir -p ./src

COPY ./src/config  ./src/config

COPY ./alembic.ini  ./alembic.ini

COPY ./src/app  ./src/app

ENV PYTHONPATH=/app/src/

CMD ["python", "src/app/main.py"]
