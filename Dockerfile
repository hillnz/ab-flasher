# renovate: datasource=docker depName=python versioning=docker
ARG PYTHON_VERSION=3.9.5
ARG BASE_IMAGE=python:${PYTHON_VERSION}

FROM --platform=${BUILDPLATFORM} python:${PYTHON_VERSION} AS poetry

# renovate: datasource=pypi depName=poetry
ARG POETRY_VERSION=1.8.4
RUN pip install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt --without-hashes >/tmp/requirements.txt

FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y e2fsprogs && \
    pip --version || apt-get install -y python3-pip

COPY --from=poetry /tmp/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# If Raspberry Pi OS then set up partitioner and service
COPY bootstrap /first_boot
RUN if grep Rasp /etc/os-release; then \
        mv /first_boot/ab-flasher.service /etc/systemd/system/ab-flasher.service && \
        systemctl enable ab-flasher.service && \
        apt-get update && apt-get install -y python3-parted && \
        sed -r -i 's! init=[^ ]+( |$)! init=/first_boot/first_boot.sh !' /boot/cmdline.txt; \
    else \
        rm -rf /first_boot; \
    fi

COPY ab-flasher /usr/local/bin/ab-flasher
ENTRYPOINT [ "ab-flasher", "--host", "/host" ]
