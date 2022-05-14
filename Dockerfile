ARG ubuntu_version
FROM ghcr.io/rse-ops/ubuntu:$ubuntu_version

# docker build --build-arg ubuntu_version=20.04 -t ghcr.io/syspack/pakages-ubuntu-20.04 .

# Convert to shallow clone (smaller container)
RUN rm -rf /opt/spack && \
   git clone --depth 1 https://github.com/spack/spack /opt/spack

# Build all software with debug flags!
ENV SPACK_ADD_DEBUG_FLAGS=true

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
