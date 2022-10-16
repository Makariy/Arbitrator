FROM python:3.9.13-slim-buster

WORKDIR /app

RUN apt update -y && apt upgrade -y

RUN apt install libpq-dev python-dev -y
RUN apt install gcc -y
ADD requirements.txt /app
RUN python -m pip install -r requirements.txt

ENV REDIS_URL "redis://redis:6379/0/"

COPY . /app
