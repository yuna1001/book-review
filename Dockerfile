FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt upgrade -y \
    && apt install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt
