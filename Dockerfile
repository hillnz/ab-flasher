# renovate: datasource=docker depName=python versioning=docker
ARG PYTHON_VERSION=3.9.2
FROM python:${PYTHON_VERSION} AS poetry

# renovate: datasource=pypi depName=poetry
ARG POETRY_VERSION=1.1.4
RUN pip install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt --without-hashes >/tmp/requirements.txt

FROM python:${PYTHON_VERSION}

RUN apt-get update && apt-get install -y \
    e2fsprogs

WORKDIR /usr/src/app

COPY --from=poetry /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "ab-flasher", "--host", "/host" ]
