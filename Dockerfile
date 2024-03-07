FROM python:3.10

COPY ./app /app
COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /app

RUN pip install -r /tmp/requirements.txt \
    && rm -rf /tmp