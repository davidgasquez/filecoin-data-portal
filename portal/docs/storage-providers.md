# Storage Providers Metrics Documentation

This documentation provides an overview of the various metrics available in the `filecoin_storage_providers.sql` file.

## General Metrics

- **provider_id**: Unique identifier for the storage provider.
- **provider_name**: Name of the storage provider.
- **region**: Geographic region of the storage provider.
- **country**: Country where the storage provider is located.
- **latitude**: Latitude coordinate of the storage provider's location.
- **longitude**: Longitude coordinate of the storage provider's location.

## Deal Metrics

- **total_deals**: Total number of deals made by the storage provider.
- **total_verified_deals**: Total number of verified deals.
- **total_active_deals**: Total number of active deals.
- **total_active_verified_deals**: Total number of active and verified deals.
- **first_deal_at**: Timestamp of the first deal.
- **first_active_deal_at**: Timestamp of the first active deal.
- **last_deal_at**: Timestamp of the most recent deal.
- **last_active_deal_at**: Timestamp of the most recent active deal.

## Data Metrics

- **total_data_uploaded_tibs**: Total data uploaded in TiBs.
- **total_active_data_uploaded_tibs**: Total active data uploaded in TiBs.
- **unique_data_uploaded_tibs**: Total unique data uploaded in TiBs.
- **unique_active_data_uploaded_tibs**: Total unique active data uploaded in TiBs.
- **unique_data_uploaded_ratio**: Ratio of unique data uploaded to total data uploaded.
- **data_uploaded_tibs_30d**: Data uploaded in the last 30 days in TiBs.
- **data_uploaded_tibs_6m**: Data uploaded in the last 6 months in TiBs.
- **data_uploaded_tibs_1y**: Data uploaded in the last year in TiBs.

## Client Metrics

- **total_unique_clients**: Total number of unique clients.
- **total_active_unique_clients**: Total number of active unique clients.
- **total_active_verified_unique_clients**: Total number of active and verified unique clients.

## Power Metrics

- **raw_power_pibs**: Raw power in PiBs.
- **quality_adjusted_power_pibs**: Quality adjusted power in PiBs.
- **verified_data_power_pibs**: Verified data power in PiBs.
- **total_sector_raw_power_tibs**: Total sector raw power in TiBs.
- **total_sector_quality_adjusted_power_tibs**: Total sector quality adjusted power in TiBs.
- **total_sealed_sector_count**: Total number of sealed sectors.
- **precommit_sector_count**: Number of precommit sectors.
- **precommit_batch_sector_count**: Number of precommit batch sectors.
- **provecommit_sector_count**: Number of provecommit sectors.
- **provecommit_batch_sector_count**: Number of provecommit batch sectors.
- **precommit_sector_raw_power_tibs**: Precommit sector raw power in TiBs.
- **precommit_sector_quality_adjusted_power_tibs**: Precommit sector quality adjusted power in TiBs.
- **provecommit_sector_raw_power_tibs**: Provecommit sector raw power in TiBs.
- **provecommit_sector_quality_adjusted_power_tibs**: Provecommit sector quality adjusted power in TiBs.
- **provecommit_batch_sector_raw_power_tibs**: Provecommit batch sector raw power in TiBs.
- **total_terminated_raw_power_tibs**: Total terminated raw power in TiBs.
- **total_terminated_quality_adjusted_power_tibs**: Total terminated quality adjusted power in TiBs.
- **total_active_terminated_raw_power_tibs**: Total active terminated raw power in TiBs.
- **total_active_terminated_quality_adjusted_power_tibs**: Total active terminated quality adjusted power in TiBs.
- **total_passive_terminated_raw_power_tibs**: Total passive terminated raw power in TiBs.
- **total_passive_terminated_quality_adjusted_power_tibs**: Total passive terminated quality adjusted power in TiBs.

## Financial Metrics

- **balance**: Current balance of the storage provider.
- **initial_pledge**: Initial pledge amount.
- **locked_funds**: Total locked funds.
- **pre_commit_deposits**: Pre-commit deposits.
- **provider_collateral**: Provider collateral.
- **fee_debt**: Fee debt.

## Performance Metrics

- **total_blocks_mined**: Total number of blocks mined.
- **total_win_count**: Total win count.
- **total_rewards_fil**: Total rewards in FIL.
- **mean_spark_retrieval_success_rate_7d**: Mean spark retrieval success rate over the last 7 days.
- **stddev_spark_retrieval_success_rate_7d**: Standard deviation of spark retrieval success rate over the last 7 days.
- **filrep_uptime_average**: Average uptime according to Filrep.
- **filrep_score**: Filrep score.
- **filrep_rank**: Filrep rank.
- **is_reachable**: Boolean indicating if the provider is reachable.
- **green_score**: Green score indicating the environmental impact.
