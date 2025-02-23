FROM python:3.10.9-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV QT_DEBUG_PLUGINS=0

ENV DEBIAN_FRONTEND=noninteractive
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1
ENV PATH="${PATH}:/root/.gem/ruby/2.7.0/bin:/root/.local/share/gem/ruby/2.7.0/bin"

RUN apt-get update && apt-get install -y build-essential python3-pip python3-dev libldap2-dev libsasl2-dev python3-pyqt5 ruby && \
    gem install fpm --user-install && \
    pip install pip==23.0.1 poetry && \
    adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser && \
    export ALINKA_VERSION=`poetry version --short` && \
    export INSTALLER_FILE_NAME="alinka-${ALINKA_VERSION}.deb"

WORKDIR /app

COPY ./alinka ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-interaction --no-root --with dev
USER qtuser
