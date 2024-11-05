FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
COPY data ./data
COPY src ./src

RUN pip install -r requirements.txt

WORKDIR /usr/src/app/src
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]