-- Local exports for FDP_DATA_URL=.generated/data, same tables as the published parquets.
copy main.daily_network_metrics to 'web/.generated/data/daily_network_metrics.parquet' (format parquet);
copy main.daily_provider_quality to 'web/.generated/data/daily_provider_quality.parquet' (format parquet);
copy main.providers to 'web/.generated/data/providers.parquet' (format parquet);
copy main.service_quarters to 'web/.generated/data/service_quarters.parquet' (format parquet);
copy main.orchestrator_quarters to 'web/.generated/data/orchestrator_quarters.parquet' (format parquet);
