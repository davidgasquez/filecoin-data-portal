# asset.description = Raw daily Filecoin market data from CoinCodex.

# asset.materialization = dataframe

# asset.column = time_start | Start timestamp of the daily price interval.
# asset.column = time_end | End timestamp of the daily price interval.
# asset.column = price_open_usd | Opening FIL price in USD.
# asset.column = price_close_usd | Closing FIL price in USD.
# asset.column = price_high_usd | Highest FIL price in USD.
# asset.column = price_low_usd | Lowest FIL price in USD.
# asset.column = price_avg_usd | Average FIL price in USD.
# asset.column = volume_usd | FIL trading volume in USD.
# asset.column = market_cap_usd | FIL market capitalization in USD.
# asset.column = price_open_btc | Opening FIL price in BTC.
# asset.column = price_close_btc | Closing FIL price in BTC.
# asset.column = price_high_btc | Highest FIL price in BTC.
# asset.column = price_low_btc | Lowest FIL price in BTC.
# asset.column = price_avg_btc | Average FIL price in BTC.
# asset.column = volume_btc | FIL trading volume in BTC.
# asset.column = market_cap_btc | FIL market capitalization in BTC.
# asset.column = price_open_eth | Opening FIL price in ETH.
# asset.column = price_close_eth | Closing FIL price in ETH.
# asset.column = price_high_eth | Highest FIL price in ETH.
# asset.column = price_low_eth | Lowest FIL price in ETH.
# asset.column = price_avg_eth | Average FIL price in ETH.
# asset.column = volume_eth | FIL trading volume in ETH.
# asset.column = market_cap_eth | FIL market capitalization in ETH.

# asset.not_null = time_start
# asset.not_null = time_end
# asset.not_null = price_avg_usd
# asset.unique = time_start
# asset.assert = time_start < time_end

import datetime as dt

import httpx
import polars as pl

START_DATE = dt.date(2020, 10, 16)
BASE_URL = (
    "https://coincodex.com/api/coincodexcoins/get_historical_data_by_slug/filecoin"
)
COLUMN_RENAMES = {
    "price_open_BTC": "price_open_btc",
    "price_close_BTC": "price_close_btc",
    "price_high_BTC": "price_high_btc",
    "price_low_BTC": "price_low_btc",
    "price_avg_BTC": "price_avg_btc",
    "volume_BTC": "volume_btc",
    "market_cap_BTC": "market_cap_btc",
    "price_open_ETH": "price_open_eth",
    "price_close_ETH": "price_close_eth",
    "price_high_ETH": "price_high_eth",
    "price_low_ETH": "price_low_eth",
    "price_avg_ETH": "price_avg_eth",
    "volume_ETH": "volume_eth",
    "market_cap_ETH": "market_cap_eth",
}


def coincodex_filecoin_market_data() -> pl.DataFrame:
    end_date = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    url = f"{BASE_URL}/{START_DATE:%Y-%m-%d}/{end_date:%Y-%m-%d}"
    payload = (
        httpx.get(url, follow_redirects=True, timeout=30).raise_for_status().json()
    )
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise TypeError("CoinCodex response is missing data rows")

    return (
        pl
        .DataFrame(rows)
        .rename(COLUMN_RENAMES)
        .with_columns(
            pl.col("time_start").str.to_datetime(),
            pl.col("time_end").str.to_datetime(),
        )
        .sort("time_start", descending=True)
    )
