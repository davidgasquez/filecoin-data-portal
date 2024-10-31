with deduplicated as (
        select
        unnest(
            max_by({{ source("raw_assets", "raw_spark_retrievals_onchain_data") }}, index, 1),
            recursive := 1
        ) as data
    from {{ source("raw_assets", "raw_spark_retrievals_onchain_data") }}
    group by date, provider_id
    order by date desc
)

select
    cast(date as date) as date,
    provider_id,
    total as total_retrieval_requests,
    successful as successful_retrieval_requests,
    successful_retrieval_requests / total_retrieval_requests as spark_retrieval_success_rate,
    cid as retrieval_result_stats_cid,
    index as retrieval_result_stats_index
from deduplicated
