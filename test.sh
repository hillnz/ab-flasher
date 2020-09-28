#!/bin/bash

docker build -t ab . && \
docker run --privileged --net=host -v /:/host ab \
    -vv \
    --host /host \
    --hash-url http://localhost:8000/os.img.sha256 \
    1.2.3 \
    http://localhost:8000/boot.tar.gz \
    sda2 \
    http://localhost:8000/os.img.gz \
    sda1,sda3
