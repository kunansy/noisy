FROM umputun/cronn:v0.3.1 as repeater

FROM python:3.10-slim-buster

COPY --from=repeater /srv/cronn /srv/cronn

RUN pip install poetry --no-cache-dir \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev -n

COPY . /app
