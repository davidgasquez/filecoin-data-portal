# :abacus: Filecoin Data Portal

Local first data hub for Filecoin, built on top of the open data stack.

The repository contains code and artifacts to help process Filecoin data from on-chain and off-chain sources. It is a simplified version of [Datadex](https://github.com/davidgasquez/datadex) allowing you to:

- See the generated dashboards and reports at [Filecoin Data Portal](https://davidgasquez.github.io/filecoin-data-portal/).
- Collaborate on [core Filecoin models](https://github.com/davidgasquez/filecoin-data-portal/blob/main/dbt/models/filecoin_state_market_deals.sql).
- Share [Filecoin related explorations with the world](https://davidgasquez.github.io/filecoin-data-portal/reports/2023-06-14-Filecoin%20JSON-RPC.html)!

## 💻 Getting Started

The easiest way to get started is to use Visuel Studio Code and rely on the Development Container configuration provided in this repository. Alternatively, you can install the dependencies locally or reuse the Dockerfile provided.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidgasquez/filecoin-data-platform)

Once in the environment, you can get the data locally with `make run` and start working with it on a notebook, model, or pipeline.

## 🛠️ Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. There are multiple interesting ways to contribute to this project:

- Add new data sources!
- Improve [dbt project](dbt/) models.
- Write a one off [report](reports/).
- Build a [dashboard](dashboards/).

## 📝 License

[MIT](https://choosealicense.com/licenses/mit/)
