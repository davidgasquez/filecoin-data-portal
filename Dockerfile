FROM mcr.microsoft.com/devcontainers/python:3.11

# Install base packages
RUN apt-get update && apt-get -y install --no-install-recommends \
    build-essential aria2 zstd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Fleek CLI
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && npm i -g @fleekxyz/cli

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_prerelease.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Environment Variables
ENV DAGSTER_HOME "/home/vscode"
ENV WORKSPACE "/workspaces/filecoin-data-portal"

# Working Directory
WORKDIR ${WORKSPACE}
