FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_download.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Setup environment
ENV DBT_PROFILES_DIR /workspaces/filecoin-analytics/dbt
ENV DATA_DIR /workspaces/filecoin-analytics/data
ENV DATABASE_URL "duckdb:///${DATA_DIR}/dbt.duckdb"

# Install Python Dependencie
WORKDIR /workspaces/filecoin-analytics
COPY . /workspaces/filecoin-analytics
RUN pip install -e ".[dev]"
