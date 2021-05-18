FROM python:3.6

ENV PYTHONPATH "${PYTHONPATH}:/utils/python-utils-ak"

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --system

COPY . /app/
RUN cd app/data && mkdir -p boiling_plan && mkdir -p schedule && mkdir -p schedule_plan && mkdir -p sku_plan && mkdir -p stats && mkdir -p templates && mkdir -p tmp
RUN mkdir /utils && cd /utils && git clone https://github.com/akadaner/python-utils-ak.git && cd python-utils-ak && git checkout 42862122ecf1594f98d0e636103d89996df60b98 && git status
EXPOSE 5000

