FROM ubuntu:22.10

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PIP_NO_CACHE_DIR="false" \
    PIP_DISABLE_PIP_VERSION_CHECK="on" \
    POETRY_VERSION="1.2.0"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python-is-python3 python3-dev \
    curl ca-certificates wait-for-it inotify-tools build-essential gettext-base && \
    rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /wetter
COPY ./wetter/pyproject.toml ./wetter/poetry.lock /wetter/

# Install dependencies

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Install actual `wetter` module

COPY . /wetter
RUN poetry install --no-interaction --no-ansi
