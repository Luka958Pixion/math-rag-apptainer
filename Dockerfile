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
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=/usr/local/go/bin:${POETRY_HOME}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV TZ=Europe/Zagreb

# Install system dependencies and timezone setup
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
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Go
RUN wget https://go.dev/dl/go${GOVERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GOVERSION}.linux-amd64.tar.gz && \
    rm go${GOVERSION}.linux-amd64.tar.gz

# Install Python 3.12
RUN add-apt-repository universe && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev && \
    rm -rf /var/lib/apt/lists/*

# Symlink python for Poetry
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

# Set working directory for build
WORKDIR /workspaces/hpc

# Copy only Poetry config for dependency install
COPY pyproject.toml poetry.lock ./

# Install project dependencies inside the container (no dev)
RUN poetry install --no-root --only main

# Copy the rest of the application code (without host-created venv)
COPY . .

# Stage 2: Runtime stage
FROM --platform=linux/amd64 ubuntu:20.04 AS runtime

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=${POETRY_HOME}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV TZ=Europe/Zagreb

# Install runtime dependencies and timezone
RUN apt-get update && \
    apt-get install -y \
      locales \
      ca-certificates \
      software-properties-common \
      tzdata \
      python3.12 && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.12 -

# Copy everything from builder (including the container-created .venv)
COPY --from=builder /workspaces/hpc /workspaces/hpc

# Set working directory
WORKDIR /workspaces/hpc

# Command to run the app
CMD ["poetry", "run", "python", "-m", "apptainer_api.main"]
