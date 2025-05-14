FROM python:3.10.9-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV QT_DEBUG_PLUGINS=0

ENV DEBIAN_FRONTEND=noninteractive
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1
ENV PATH="${PATH}:/root/.gem/ruby/2.7.0/bin:/root/.local/share/gem/ruby/2.7.0/bin"

# This is needed to install qt6-base-dev on bullseye
RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y build-essential python3-pip python3-dev libxcb-cursor0 qt6-base-dev ruby && \
    gem install fpm --user-install && \
    pip install pip==23.0.1 poetry && \
    adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

WORKDIR /app

COPY ./alinka ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-interaction --no-root --with dev
USER qtuser
