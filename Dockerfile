ARG ubuntu_version=20.04
FROM ubuntu:$ubuntu_version
ARG CMAKE=3.20.4

# docker build --build-arg ubuntu_version=20.04 -t ghcr.io/syspack/pakages-ubuntu-20.04 .

# Build all software with debug flags!
ENV SPACK_ADD_DEBUG_FLAGS=true
ENV PATH=/opt/spack/bin:$PATH

# Ubuntu dependencies
RUN apt-get update && apt-get install -y wget && \
    wget https://raw.githubusercontent.com/rse-ops/docker-images/main/scripts/ubuntu/apt-install-defaults-plus-args.sh && \
    chmod +x apt-install-defaults-plus-args.sh && \
    ./apt-install-defaults-plus-args.sh && \
    rm apt-install-defaults-plus-args.sh

# Install cmake binary
RUN curl -s -L https://github.com/Kitware/CMake/releases/download/v$CMAKE/cmake-$CMAKE-linux-x86_64.sh > cmake.sh && \
    sh cmake.sh --prefix=/usr/local --skip-license && \
    rm cmake.sh

# And spack deps
RUN git clone --depth 1 https://github.com/spack/spack /opt/spack && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install clingo && \
    spack external find && \
    spack external find python perl binutils git tar xz bzip2 && \
    
    # build for a generic target
    spack config add 'packages:all:target:[x86_64]' && \

    # reuse as much as possible, make externals useful
    spack config add 'concretizer:reuse:true'

# install oras so we don't need to bootstrap
RUN curl -LO https://github.com/oras-project/oras/releases/download/v0.12.0/oras_0.12.0_linux_amd64.tar.gz && \
    mkdir -p oras-install/ && \
    tar -zxf oras_0.12.0_*.tar.gz -C oras-install/ && \
    mv oras-install/oras /usr/local/bin/ && \
    rm -rf oras_0.12.0_*.tar.gz oras-install/

# The entrypoint.sh is called during the ci
COPY ./entrypoint.sh /entrypoint.sh
WORKDIR /opt/pakages
COPY . /opt/pakages
RUN python3 -m pip install .

ENV SPACK_ROOT=/opt/spack    
ENTRYPOINT ["/bin/bash"]
