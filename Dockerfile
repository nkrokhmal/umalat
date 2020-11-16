FROM python:3.6 AS builder
WORKDIR /install
COPY requirements.txt /install
RUN pip install --install-option="--prefix=/install" -r requirements.txt

FROM python:3.6-alpine
COPY --from=builder /install /usr/local

WORKDIR /app
COPY ./app .
COPY config.py .
COPY data.sqlite .
COPY manage.py .
COPY data .

EXPOSE 8000

cmd ["python", "manage.py", "runserver"]
