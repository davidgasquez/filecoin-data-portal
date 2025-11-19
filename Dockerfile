FROM mcr.microsoft.com/devcontainers/python:3.12

# Install base packages
RUN apt-get update && apt-get -y install --no-install-recommends \
    build-essential aria2 zstd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Environment Variables
ENV DAGSTER_HOME "/home/vscode"
ENV WORKSPACE "/workspaces/filecoin-data-portal"

# Working Directory
WORKDIR ${WORKSPACE}
