FROM python:3.6-slim-buster
LABEL maintainer="Peter Andersen <swarfarm@porksmash.com>"

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements_dev.txt requirements_dev.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV BUILD_DEPS="build-essential" \
    APP_DEPS="netcat curl libpq-dev"

ARG PRODUCTION

RUN apt-get update \
  && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends \
  && if [ "$PRODUCTION" = "True" ]; then pip install -r requirements.txt; else pip install -r requirements_dev.txt; fi \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  && apt-get clean

COPY . .

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
