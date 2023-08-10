with base as (
    select
        unnest(data) as row
    from read_json_auto('https://api.datacapstats.io/api/getVerifiedClients')
)

select
    row ->> 'id' as id,
    row ->> 'addressId' as addressid,
    row ->> 'address' as address,
    row ->> 'retries' as retries,
    row ->> 'auditTrail' as audittrail,
    row ->> 'name' as name,
    row ->> 'orgName' as orgname,
    row ->> 'region' as region,
    row ->> 'website' as website,
    row ->> 'industry' as industry,
    row ->> 'initialAllowance' as initialallowance,
    row ->> 'allowance' as allowance,
    row ->> 'verifierAddressId' as verifieraddressid,
    row ->> 'createdAtHeight' as createdatheight,
    row ->> 'issueCreateTimestamp' as issuecreatetimestamp,
    row ->> 'createMessageTimestamp' as createmessagetimestamp,
    row ->> 'verifierName' as verifiername,
    row ->> 'dealCount' as dealcount,
    row ->> 'providerCount' as providercount,
    row ->> 'topProvider' as topprovider,
    row ->> 'receivedDatacapChange' as receiveddatacapchange,
    row ->> 'usedDatacapChange' as useddatacapchange,
    row ->> 'allowanceArray' as allowancearray
from base
