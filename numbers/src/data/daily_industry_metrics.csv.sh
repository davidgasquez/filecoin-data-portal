#!/usr/bin/env bash

duckdb :memory: << EOF
SET enable_progress_bar = false;
COPY (
    select
        m.date,
        c.industry,
        sum(m.onboarded_data_tibs) as onboarded_data_tibs,
    from read_parquet('https://data.filecoindataportal.xyz/filecoin_daily_clients_metrics.parquet') as m
    left join read_parquet('https://data.filecoindataportal.xyz/filecoin_clients.parquet') as c on m.client_id = c.client_id
    group by all
    order by date desc, industry desc
) TO STDOUT (FORMAT 'CSV');
EOF
