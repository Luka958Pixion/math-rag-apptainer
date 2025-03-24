# Stage 1: Build stage
FROM ubuntu:20.04 AS builder

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    GOVERSION=1.21.0 \
    PYTHON_VERSION=3.12.7 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Go
RUN wget https://go.dev/dl/go${GOVERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GOVERSION}.linux-amd64.tar.gz && \
    rm go${GOVERSION}.linux-amd64.tar.gz

# Install Python 3.12.7
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

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
    python${PYTHON_VERSION} --version && \
    poetry --version && \
    apptainer --version

# Set working directory
WORKDIR /root

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . .

# Stage 2: Runtime stage
FROM ubuntu:20.04 AS runtime

# Environment variables
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    PYTHON_VERSION=3.12.7 \
    POETRY_HOME="/opt/poetry" \
    PATH="$POETRY_HOME/bin:$PATH" \
    VIRTUAL_ENV="/root/.venv" \
    PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    locales \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Python 3.12.7
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy virtual environment from builder stage
COPY --from=builder /root/.venv /root/.venv

# Copy application code
COPY --from=builder /root /root

# Set working directory
WORKDIR /root

# Command to run the application
CMD ["python", "-m", "apptainer_api.main"]

