FROM mcr.microsoft.com/devcontainers/python:3.11

# Install base packages
RUN apt-get update && apt-get -y install --no-install-recommends \
    build-essential aria2 zstd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_prerelease.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Working Directory
ENV WORKSPACE "/workspaces/filecoin-data-portal"
WORKDIR ${WORKSPACE}

# Environment Variables
ENV PROJECT_DIR "${WORKSPACE}"
ENV DATA_DIR "${WORKSPACE}/data"
ENV DBT_PROFILES_DIR "${WORKSPACE}/dbt"
ENV DATABASE_URL "duckdb:///${DATA_DIR}/local.duckdb"
ENV DAGSTER_HOME "/home/vscode"
