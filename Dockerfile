FROM python:3.12-slim

ENV PYTHONUNBUFFERED True

WORKDIR /usr/src/app

COPY requirements.txt .
COPY data ./data
COPY src ./src

RUN pip install -r requirements.txt

WORKDIR /usr/src/app/src

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:server"]

