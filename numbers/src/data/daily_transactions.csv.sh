#!/usr/bin/env bash

duckdb :memory: << EOF
SET enable_progress_bar = false;
COPY (
    select
        date,
        method,
        gas_used_millions,
        transactions
    from read_parquet('https://data.filecoindataportal.xyz/filecoin_daily_transactions.parquet')
) TO STDOUT (FORMAT 'CSV');
EOF
