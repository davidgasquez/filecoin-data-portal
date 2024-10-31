<p align="center">
  <div align="center">
    <img width="80px" src="https://filecoindataportal.xyz/logo.svg">
  </div>
  <h1 align="center">Filecoin Data Portal</h1>
  <p align="center">Open, serverless, and local friendly Data Platform for the Filecoin Ecosystem.</a> </p>
</p>

<div align="center">
  <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/davidgasquez/filecoin-data-portal/pipeline.yml?style=flat-square">
  <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/davidgasquez/filecoin-data-portal/tables.yml?style=flat-square">
  <img alt="GitHub" src="https://img.shields.io/github/license/davidgasquez/filecoin-data-portal?style=flat-square">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/davidgasquez/filecoin-data-portal?style=flat-square">
</div>

<br>

## 📖 Overview

This repository contains all the code and related artifacts to process Filecoin data from [diverse sources](portal/docs/data-sources.md) (on-chain and off-chain). You can go directly to the processed datasets or explore the different metrics and pipelines.

<div align="center">
  <a href="https://filecoindataportal.xyz/data" target="_blank">
      <img src="https://img.shields.io/badge/GET_THE_DATA-0090ff?style=for-the-badge" alt="GET THE DATA">
  </a>
</div>

### 📦 Key Features

- **Open**: Code and data are open source and relies on open standards and formats.
- **Permissionless Collaboration**: Collaborate on data, models, and pipelines. Fork the repo and run the platform locally in mintures. No constraints or platform lock-ins.
- **Decentralization Options**: Runs on a laptop, server, CI runner, or even on decentralized compute networks like Bacalhau. No local setup required; it even works seamlessly in GitHub Codespaces.
- **Data as Code**: Each commit generates and pushes all table files to R2.
- **Modular Flexibility**: Replace, extend, or remove individual components. Compatible with tons of tools. At the end of the day, tables are Parquet files.
- **Low Friction Data Usage**: Raw and processed data is available to anyone openly. Use whatever tool you want!
- **Modern Data Engineering**: Supports data engineering essentials such as typing, testing, materialized views, and development branches. Utilizes best practices, including declarative transformations, and utilizes state-of-the-art tools like DuckDB.

## 🚀 Powering

- [Filecoin Pulse Website](https://pulse.filecoindataportal.xyz/)
- [Filecoin Metrics Dune Dashboard](https://dune.com/kalen/filecoin-daily-metrics)

## 🛠️ Contributing

This project is in active development. You can help by giving ideas, answering questions, reporting bugs, proposing enhancements, improving the documentation, and fixing bugs. Feel free to open issues and pull requests!

Some ways you can contribute to this project:

- Adding new data sources.
- Improving the data quality of existing datasets.
- Adding tests to the data pipelines.

## ⚙️ Development

You can run the Filecoin Data Portal locally using Python Virtual Environment or VSCode Development Containers. You'll need the following secrets in your environment:

- A `SPACESCOPE_TOKEN` to access [Spacescope](https://spacescope.io/) API.
- A Google Cloud Platform `GOOGLE_APPLICATION_CREDENTIALS` for accessing BigQuery.
- A `SPARK_API_BEARER_TOKEN` for accessing Spark retrievals API.
- A `DUNE_API_KEY` for accessing Dune Analytics.

### 🐍 Python Virtual Environment

Clone the repository and run the following commands (or `make setup`) from the root folder:

```bash
# Create a virtual environment
pip install uv && uv venv

# Install the package and dependencies
uv pip install -U -e .[dev]
```

Now, you should be able to spin up Dagster UI (`make dev`) and [access it locally](http://127.0.0.1:3000).

### 🐳 Dev Container

You can jump into the repository [Development Container](https://code.visualstudio.com/docs/remote/containers). Once inside the develpment environment, you'll only need to run `make dev` to spin up the [Dagster UI locally](http://127.0.0.1:3000). The development environment can also run in your browser thanks to GitHub Codespaces!

[![Development Container Badge](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidgasquez/filecoin-data-portal)

## 📃 Disclaimer

The datasets provided by this service are made available "as is", without any warranties or guarantees of any kind, either expressed or implied. By using these datasets, you agree that you do so at your own risk.

## 📝 License

[MIT](https://choosealicense.com/licenses/mit/)
