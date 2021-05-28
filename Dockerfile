FROM python:3.7

ENV PYTHONPATH "${PYTHONPATH}:/utils/python-utils-ak"

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install
RUN mkdir /utils && cd /utils && git clone https://github.com/akadaner/python-utils-ak.git

COPY . /app/
EXPOSE 5000
