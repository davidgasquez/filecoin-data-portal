dealbot_payers as (
    select distinct lower(json_extract_string(args, '$.payer')) as payer
    from raw.riba_eth_logs_decoded
    where contract_name = 'filecoin_warm_storage_service'
      and event_name = 'DataSetCreated'
      and (
          list_contains(json_extract_string(args, '$.metadataKeys[*]'), 'dealbotDS')
          or json_extract_string(args, '$.metadataValues[*]')[
              list_position(json_extract_string(args, '$.metadataKeys[*]'), 'source')
          ] = 'dealbot'
      )
)
