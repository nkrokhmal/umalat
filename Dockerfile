FROM python:3.7

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY . /app/
EXPOSE 5000
