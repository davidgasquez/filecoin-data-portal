# Using Portal's Datasets

The Filecoin Data Portal publishes up to date dataset on a daily bases as [static Parquet files at `/data`](https://filecoindataportal.davidgasquez.com/data). You can then use any tool you want to explore and use these datasets! Let's go through some examples.

## Python

You can use the `pandas` library to read the Parquet files. Here's an example:

```python
import pandas as pd

url = 'https://filecoindataportal.davidgasquez.com/data/filecoin_daily_metrics.parquet'
df = pd.read_parquet(url)
print(df)
```

You can play with the datasets in Google Colab for free. Check this sample notebook.

<a target="_blank" href="https://colab.research.google.com/drive/1u0XAWi2wrnEOiEXFVrfYmt0M1qJXPxRt">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

## JavaScript

You can use the [`duckdb` Obervable client](https://observablehq.com/@cmudig/duckdb-client) library to read the Parquet files and run SQL queries on them. Here's an example:

```javascript
db = DuckDBClient.of({})

db.query(`
    select
    *
    from "https://filecoindataportal.davidgasquez.com/data/filecoin_daily_metrics.parquet"
`)
```

Check this [sample Observable JS notebook](https://observablehq.com/@davidgasquez/fdp) to see how to explore and visualize the datasets.

## Dune

Some of the datasets built by the pipelines are also available in Dune. You can use the Dune SQL editor to run queries on these datasets. [Here's an example](https://dune.com/queries/3302707/5958324):

```sql
select
  date,
  onboarded_data_pibs,
  unique_data_onboarded_data_pibs,
  data_on_active_deals_pibs,
  unique_data_on_active_deals_pibs,
  deals
from dune.kalen.dataset_filecoin_daily_metrics
```

## Google Sheets

The pipelines that are executed to generate the datasets are also pushing the data to Google Sheets. You can access the data directly from these Google Sheets:

- [Filecoin Daily Metrics](https://docs.google.com/spreadsheets/d/1uq9J_WTJO6kAvQlrqkqR8GHfQfh3SJ84OSj88Mff6vY)
- [Filecoin Storage Providers](https://docs.google.com/spreadsheets/d/1hC5HwuiqQvQcVvV06n3SH0wKkZwbw20EufGYHSyENs0)
- [Filecoin Clients](https://docs.google.com/spreadsheets/d/15xi39OheVJ-_WyI7sxwmvgMIVFkZN07NOYWLe5iKXnI)
- [Filecoin Allocators](https://docs.google.com/spreadsheets/d/1uixeylC3pTeOkKh0L2fGsd7YKuyaA6Hse_fhWrm1BIA)

You can create a new personal Google Sheet and use the [`IMPORTRANGE` function](https://support.google.com/docs/answer/3093340?hl=en) to read data from these sheets and be able to plot or add more transformations on top.

## BI Tools

Depending on the BI tool you are using, you can connect to the Parquet files directly, use the Google Sheets as a data source, or you'll need to load the data into a database like PostgreSQL or BigQuery. There are

### Evidence

[Filecoin Pulse](https://filecoinpulse.pages.dev/) is a website build with Evidence using the Filecoin Data Portal datasets. You can [check the source code on GitHub](https://github.com/davidgasquez/filecoin-pulse) to see how to use the datasets in Evidence.

### Observable Framework

Another alternative is to use the Observable framework to create dashboards and visualizations. You can use parquet files as data sources and generate beautiful static websites providing dashboards and reports like [Filecoin Metrics](https://davidgasquez.github.io/filecoin-metrics/), a proof of concept dashboard built with Observable Framework. You can check the [source code on GitHub](https://github.com/davidgasquez/filecoin-metrics) too.

## Others

Do you have any other tool you want to use to explore the datasets? [Reach out](https://github.com/davidgasquez/filecoin-data-portal/issues/new) and let's explore how to use the datasets with your favorite tools!
