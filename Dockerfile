FROM python:3.8.5-slim

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT [ "python", "ab-flasher", "--host", "/host" ]
