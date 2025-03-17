FROM ubuntu:20.04

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
    gcc \
    g++ \
    nano \
    qemu-user-static \
    yq \
    && rm -rf /var/lib/apt/lists/*

# Generate and configure UTF-8 locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Go for amd64
ENV GOVERSION=1.21.0
RUN wget https://go.dev/dl/go${GOVERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GOVERSION}.linux-amd64.tar.gz && \
    rm go${GOVERSION}.linux-amd64.tar.gz

# Set Go environment variables
ENV PATH=$PATH:/usr/local/go/bin

# Verify Go installation
RUN go version

# Install Apptainer
RUN wget https://github.com/apptainer/apptainer/releases/download/v1.3.6/apptainer-1.3.6.tar.gz && \
    tar -xzf apptainer-1.3.6.tar.gz && \
    cd apptainer-1.3.6 && \
    export CC=gcc && \
    export CXX=g++ && \
    export GOARCH=amd64 && \
    ./mconfig --without-suid && \
    make -C builddir && \
    make -C builddir install && \
    cd .. && rm -rf apptainer-1.3.6*

# Verify Apptainer installation
RUN apptainer --version

# Copy data_stack.def into the container
COPY data_stack.def /root/data_stack.def

# Copy requirements.txt into the container
COPY requirements.txt /root/requirements.txt

# Set working directory
WORKDIR /root
