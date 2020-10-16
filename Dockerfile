FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /code/
WORKDIR /code/

RUN apt-get update && apt-get install -y postgresql-client

RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . .