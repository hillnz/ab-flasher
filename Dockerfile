# renovate: datasource=docker depName=python versioning=docker
ARG PYTHON_VERSION=3.9.4
ARG BASE_IMAGE=python:${PYTHON_VERSION}

FROM --platform=${BUILDPLATFORM} python:${PYTHON_VERSION} AS poetry

# renovate: datasource=pypi depName=poetry
ARG POETRY_VERSION=1.1.5
RUN pip install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt --without-hashes >/tmp/requirements.txt

FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y e2fsprogs && \
    pip --version || apt-get install -y python3-pip

WORKDIR /usr/src/ab-flasher

COPY --from=poetry /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# If systemd (if a real image) then set it up to run as a service
COPY ab-flasher.service /tmp
RUN if [[ -d /etc/systemd/system ]]; then \
        cp ab-flasher.service /etc/systemd/system/ab-flasher.service && \
        systemctl enable ab-flasher.service \
    fi; \
    rm /tmp/ab-flasher.service

ENTRYPOINT [ "python", "ab-flasher", "--host", "/host" ]
