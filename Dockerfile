FROM python:3.6

ENV PYTHONPATH "${PYTHONPATH}:/utils/python-utils-ak"

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --system

COPY . /app/
RUN cd app/data && mkdir -p boiling_plan && mkdir -p schedule && mkdir -p schedule_plan && mkdir -p sku_plan && mkdir -p stats && mkdir -p templates && mkdir -p tmp
RUN mkdir /utils && cd /utils && git clone https://github.com/akadaner/python-utils-ak.git
EXPOSE 5000

