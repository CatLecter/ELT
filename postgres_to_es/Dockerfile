FROM python:3.9.10-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 8000

WORKDIR /usr/src/etl

COPY ./requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
#    && apt update \
#    && apt install -y systemd redis-server \
#    && service redis-server start \
#    && service redis-server status

COPY . .

CMD celery -A tasks worker -B --loglevel=info