# Stage 1: Build stage
FROM --platform=linux/amd64 ubuntu:20.04 AS builder

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV GOVERSION=1.21.0
ENV POETRY_VERSION=2.1.1
ENV POETRY_HOME=/opt/poetry
ENV VIRTUAL_ENV=/root/.venv
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=/usr/local/go/bin:${POETRY_HOME}/bin:${VIRTUAL_ENV}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV TZ=Europe/Zagreb

# Install system dependencies and set timezone non-interactively
RUN apt-get update && \
    apt-get install -y \
    wget \
    build-essential \
    libseccomp-dev \
    pkg-config \
    squashfs-tools \
    cryptsetup \
    uidmap \
    git \
    locales \
    tzdata \
    ca-certificates \
    gcc \
    g++ \
    nano \
    qemu-user-static \
    curl \
    software-properties-common && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Go
RUN wget https://go.dev/dl/go${GOVERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GOVERSION}.linux-amd64.tar.gz && \
    rm go${GOVERSION}.linux-amd64.tar.gz

# Install Python 3.12 (with venv support)
RUN add-apt-repository universe && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a symlink for 'python' so that Poetry can find it
RUN ln -s /usr/bin/python3.12 /usr/local/bin/python

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.12 -

# Install Apptainer
RUN wget https://github.com/apptainer/apptainer/releases/download/v1.3.6/apptainer-1.3.6.tar.gz && \
    tar -xzf apptainer-1.3.6.tar.gz && \
    cd apptainer-1.3.6 && \
    ./mconfig --without-suid && \
    make -C builddir && \
    make -C builddir install && \
    cd .. && rm -rf apptainer-1.3.6*

# Verify installations
RUN go version && \
    python3.12 --version && \
    poetry --version && \
    apptainer --version

# Set working directory
WORKDIR /root

# Copy Poetry dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install project dependencies (main only, no dev)
RUN poetry install --no-root --only main

# Copy the rest of the application code (includes the .venv directory)
COPY . .

# Stage 2: Runtime stage
FROM --platform=linux/amd64 ubuntu:20.04 AS runtime

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV POETRY_HOME=/opt/poetry
ENV VIRTUAL_ENV=/root/.venv
ENV PATH=${POETRY_HOME}/bin:${VIRTUAL_ENV}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV TZ=Europe/Zagreb

# Install runtime dependencies and configure timezone
RUN apt-get update && \
    apt-get install -y \
    locales \
    ca-certificates \
    software-properties-common \
    tzdata \
    python3.12 && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Copy application code and virtual environment from builder
COPY --from=builder /root /root

# Set working directory
WORKDIR /root

# Command to run the app
CMD ["python3.12", "-m", "apptainer_api.main"]
