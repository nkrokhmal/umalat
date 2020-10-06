from python:3.6

WORKDIR /app
COPY . /app
RUN pip install -r /app/requirements.txt

EXPOSE 8000

cmd ["python", "manage.py"]
