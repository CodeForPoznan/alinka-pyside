FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV QT_DEBUG_PLUGINS=0

ENV DEBIAN_FRONTEND=noninteractive
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1
ENV PATH="${PATH}:/root/.gem/ruby/3.3.0/bin:/root/.local/share/gem/ruby/3.3.0/bin"

RUN apt-get update && apt-get install -y build-essential python3-pip python3-dev libxcb-cursor0 qt6-base-dev ruby git curl && \
    gem install fpm --user-install && \
    pip install pip==25.1.1 poetry setuptools && \
    curl -sL https://www.openssl.org/source/openssl-1.1.1b.tar.gz | tar xzf - && \
    cd openssl-1.1.1b && ./config --prefix=/usr/local/ --openssldir=/usr/local/ zlib -fPIC shared && make && make install && cd .. && \
    git clone https://github.com/sqlcipher/sqlcipher && cd sqlcipher && ./configure --disable-tcl LDFLAGS="-lcrypto -lm" && make sqlite3.c && cd .. && \
    git clone https://github.com/coleifer/sqlcipher3 && cp sqlcipher/sqlite3.[ch] sqlcipher3/ && cd sqlcipher3 && python setup.py build_static build && \
    adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

WORKDIR /app

COPY ./alinka ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-interaction --no-root --with dev
USER qtuser
