# One image for every role (superlink, supernode, dashboard). Multi-arch: linux/amd64 and linux/s390x (IBM LinuxONE).
# Build from the repo root:  docker build -f deploy/Dockerfile -t zero-exposure-fl .
#                            docker buildx build --platform linux/s390x -f deploy/Dockerfile -t zero-exposure-fl:s390x .
FROM ubuntu:24.04

# PIP_DEFAULT_TIMEOUT / PIP_RETRIES: a 15 s read timeout killed the first s390x build while it fetched build dependencies.
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=10

# numpy / scipy / pandas / scikit-learn come from apt: PyPI has no s390x wheels for them, Ubuntu ships s390x builds.
# The compiler, Rust and the -dev packages are for grpcio / cryptography / pycryptodome, which pip must build from source on s390x.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-dev python3-pip \
        python3-numpy python3-scipy python3-pandas python3-sklearn \
        build-essential pkg-config libssl-dev libffi-dev zlib1g-dev libc-ares-dev rustc cargo ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --system-site-packages: the venv sees the apt numpy/scipy/pandas/sklearn instead of rebuilding them.
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# torch: CPU wheels for amd64 AND s390x only exist on this index (not on PyPI for s390x).
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
# grpcio and cryptography have no s390x wheels on PyPI: pip compiles them (hours under QEMU, minutes on a real LinuxONE VM).
# One RUN each, so a failure in one does not throw away the other's cached layer. On amd64 pip just downloads wheels.
#  * GRPC_PYTHON_BUILD_SYSTEM_*: link grpcio against Ubuntu's OpenSSL / zlib / c-ares instead of building BoringSSL (BoringSSL's
#    s390x support is not something to rely on) and the bundled copies: a much shorter compile.
#  * MAKEFLAGS / GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS: parallel compile jobs (4: more can run out of memory in a small Docker VM).
RUN GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1 GRPC_PYTHON_BUILD_SYSTEM_CARES=1 \
    GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=4 MAKEFLAGS=-j4 \
    pip install "grpcio>=1.70.0,<2.0.0" "grpcio-health-checking>=1.70.0,<2.0.0"
RUN MAKEFLAGS=-j4 CARGO_BUILD_JOBS=4 pip install "cryptography>=46.0.7,<47.0.0"
# flwr 1.37 also brings fastapi and uvicorn. No ray: deployment mode does not use the simulation engine.
RUN pip install flwr==1.37.0 opacus==1.6.0

# torch's s390x wheel links libopenblas.so.0 dynamically (`import torch` failed with ImportError without it; the apt scipy only pulls
# the slow reference BLAS). Its own layer, so the hours-long compile layers above stay cached when this list changes.
RUN apt-get update && apt-get install -y --no-install-recommends libopenblas0 && rm -rf /var/lib/apt/lists/*

# protobuf's C extension (upb) segfaults on import on s390x (seen under QEMU: `import flwr` dies in google.protobuf.internal.builder).
# A .pth line runs at every Python start-up and selects the pure-Python implementation there (correct on any byte order, slower).
RUN printf '%s\n' 'import os, platform; platform.machine() == "s390x" and os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")' > /opt/venv/lib/python3.12/site-packages/s390x-protobuf.pth

# Flower sends usage telemetry and checks for new versions over the network by default: off (privacy demo; LinuxONE VMs may be offline).
ENV FLWR_TELEMETRY_ENABLED=0 FLWR_DISABLE_UPDATE_CHECK=1

WORKDIR /app
COPY . /app
# Flower home: the CLI config for the dashboard container (superlink:9093) and the writable cache of every Flower process.
ENV FLWR_HOME=/flwr_home

# Run as the unprivileged user that ubuntu:24.04 ships (uid 1000). /runs is the folder shared with the dashboard.
RUN mkdir -p /runs /data /flwr_home && cp /app/deploy/flwr_home/config.toml /flwr_home/config.toml \
    && chown -R ubuntu:ubuntu /runs /data /flwr_home
USER ubuntu
ENV HOME=/home/ubuntu
EXPOSE 8000 9092 9093
