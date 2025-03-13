FROM ubuntu:20.04 AS base

# Set environment variables for UTF-8
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US:en

# Install dependencies
RUN apt update && apt install -y \
    wget \
    build-essential \
    libseccomp-dev \
    pkg-config \
    squashfs-tools \
    cryptsetup \
    uidmap \
    git \
    locales \
    ca-certificates \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Generate and configure UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Go (latest stable version)
ENV GOVERSION=1.21.0
RUN wget https://go.dev/dl/go${GOVERSION}.linux-arm64.tar.gz && \
    tar -C /usr/local -xzf go${GOVERSION}.linux-arm64.tar.gz && \
    rm go${GOVERSION}.linux-arm64.tar.gz

# Set Go environment variables
ENV PATH=$PATH:/usr/local/go/bin

# Verify Go installation
RUN go version

# Download and install Apptainer
RUN wget https://github.com/apptainer/apptainer/releases/download/v1.3.6/apptainer-1.3.6.tar.gz && \
    tar -xzf apptainer-1.3.6.tar.gz && \
    cd apptainer-1.3.6 && \
    export CC=aarch64-linux-gnu-gcc && \
    export CXX=aarch64-linux-gnu-g++ && \
    export GOARCH=arm64 && \
    ./mconfig --without-suid && \
    make -C builddir && \
    make -C builddir install && \
    cd .. && rm -rf apptainer-1.3.6*

# Verify Apptainer installation
RUN apptainer --version

# Copy data_stack.def file
COPY data_stack.def /root/data_stack.def

# Set working directory
WORKDIR /root
