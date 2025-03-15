FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

COPY . .
