# One image for every role (superlink, supernode, dashboard). Multi-arch: linux/amd64 and linux/s390x (IBM LinuxONE).
# Build from the repo root:  docker build -f deploy/Dockerfile -t zero-exposure-fl .
#                            docker buildx build --platform linux/s390x -f deploy/Dockerfile -t zero-exposure-fl:s390x .
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONUNBUFFERED=1

# numpy / scipy / pandas / scikit-learn come from apt: PyPI has no s390x wheels for them, Ubuntu ships s390x builds.
# The compiler, Rust and the -dev packages are for grpcio / cryptography / pycryptodome, which pip must build from source on s390x.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-dev python3-pip \
        python3-numpy python3-scipy python3-pandas python3-sklearn \
        build-essential pkg-config libssl-dev libffi-dev rustc cargo ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --system-site-packages: the venv sees the apt numpy/scipy/pandas/sklearn instead of rebuilding them.
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# torch: CPU wheels for amd64 AND s390x only exist on this index (not on PyPI for s390x).
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
# flwr 1.37 brings grpcio, cryptography, fastapi, uvicorn. No ray: deployment mode does not use the simulation engine.
RUN pip install flwr==1.37.0 opacus==1.6.0

WORKDIR /app
COPY . /app
# Flower home: the CLI config for the dashboard container (superlink:9093) and the writable cache of every Flower process.
ENV FLWR_HOME=/flwr_home

# Run as the unprivileged user that ubuntu:24.04 ships (uid 1000). /runs is the folder shared with the dashboard.
RUN mkdir -p /runs /data /flwr_home && cp /app/deploy/flwr_home/config.toml /flwr_home/config.toml     && chown -R ubuntu:ubuntu /runs /data /flwr_home
USER ubuntu
ENV HOME=/home/ubuntu
EXPOSE 8000 9092 9093
