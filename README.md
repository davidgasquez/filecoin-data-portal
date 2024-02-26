# 🗂️ Filecoin Data Portal

[![CI](https://github.com/davidgasquez/filecoin-data-portal/actions/workflows/ci.yml/badge.svg)](https://github.com/davidgasquez/filecoin-data-portal/actions/workflows/ci.yml)

Open source, serverless, and local-first Data Platform for the Filecoin ecosystem. The goal with this portal is to improve data access and empower more people conducting research to drives the community forward!

![DAG](https://github.com/davidgasquez/filecoin-data-portal/assets/1682202/581155f3-0d23-45fa-a67a-bb373df7078a)

Check out the [Filecoin Data Portal](https://filecoin-data-portal.on-fleek.app/) website for dashboards and reports!

## 📂 Data

The data lives under the [IPFS CID](https://raw.githubusercontent.com/davidgasquez/filecoin-data-portal/main/data/IPFS_CID) pointer available in this repository and the [`ipns://k51qzi5uqu5dh0eqsyw9shepsspstaduq8lgnept49epxvo4t8qfi6ridcmt8k`](https://ipfs.io/ipns/k51qzi5uqu5dh0eqsyw9shepsspstaduq8lgnept49epxvo4t8qfi6ridcmt8k/) IPNS address.

<center>

<a href="https://ipfs.io/ipns/k51qzi5uqu5dh0eqsyw9shepsspstaduq8lgnept49epxvo4t8qfi6ridcmt8k/" target="_blank">
    <img src="https://img.shields.io/badge/GET_THE_DATA-0090ff?style=for-the-badge" alt="GET THE DATA">
</a>

</center>

## 📖 Overview

This repository contains code and artifacts to help anyone process Filecoin data from [diverse sources](portal/docs/data-sources.md) (on-chain and off-chain). It is an implementation of [Datadex](https://github.com/davidgasquez/datadex), allowing anyone to collaborate on data, models, and pipelines in a permissionless way.

### 📦 Key Features

- **Open**
  - All code and data are open source.
  - Utilizes open standards and formats within the Arrow ecosystem.
- **Permissionless Collaboration**
  - Collaborate on data, models, and pipelines like Dune, but with open-source freedom.
  - No constraints from private APIs or platform lock-ins.
  - Enjoy full Git features such as branching, merging, and pull requests.
- **Decentralization Options**
  - Run the project on a laptop, server, CI runner, or even on decentralized compute networks like Bacalhau.
  - No local setup required; it even works seamlessly in GitHub Codespaces.
  - Data is stored in IPFS, where datasets will become more distributed as more users run it.
  - Multiple data sources and flexible exposure options.
- **Data as Code**
  - Each commit generates and pushes all table files to IPFS.
  - Easily access historical data snapshots.
  - Declarative and stateless transformations tracked in git.
  - Static dashboards and reports available at the [Filecoin Data Portal](https://filecoin-data-portal.on-fleek.app/).
- **Modular Flexibility**
  - Replace, extend, or remove individual components.
  - Works across various environments (laptop, cluster, browser).
  - Compatible with tons of tools. At the end of the day, tables are Parquet/CSV files.
- **Low Friction Data Usage**
  - Raw and processed data is available to anyone on IPFS. Use wathever tool you want!
  - Get started with simple actions like pasting a [SQL query in your browser](https://shell.duckdb.org/) or using `pd.read_parquet(url)` in a Notebook.
  - [Static Quarto Notebooks with embedded datasets](https://filecoin-data-portal.on-fleek.app/reports/2023-06-21-Exploring-Filecoin-Deals.html) are generated with every commit, serving as documentation or a simple reporting/dashboarding layer.
- **Modern Data Engineering**
  - Supports data engineering essentials such as typing, testing, materialized views, and development branches.
  - Utilizes best practices, including declarative transformations, and utilizes state-of-the-art tools like DuckDB.

## 🛠️ Contributing

This project is in active development. You can help by giving ideas, answering questions, reporting bugs, proposing enhancements, improving the documentation, and fixing bugs. Feel free to open issues and pull requests!

Some ways you can contribute to this project:
- Adding new data sources.
- Improving the data quality of existing datasets.
- Adding tests to the data pipelines.

## ⚙️ Development

You can run the entire Filecoin Data Portal locally using Python Virtual Environment or VSCode Development Containers. You'll need the following secrets in your environment:

- A `SPACESCOPE_TOKEN` to access [Spacescope](https://spacescope.io/) API.

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

[![](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidgasquez/filecoin-data-portal)

## 📝 License

[MIT](https://choosealicense.com/licenses/mit/)
