FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

COPY ./src/app  ./app

COPY ./src/config  ./config

ENV PYTHONPATH=/app

CMD ["python", "app/main.py"]
