with base as (
    select
        unnest(miners) as m
    from read_json_auto('https://api.filrep.io/api/v1/miners')
)

select
    m ->> 'address' as address,
    m ->> 'status' as status,
    m ->> 'reachability' as reachability,
    m ->> 'tag' as tag,
    m ->> 'uptimeAverage' as uptimeaverage,
    m ->> 'price' as price,
    m ->> 'verifiedPrice' as verifiedprice,
    m ->> 'minPieceSize' as minpiecesize,
    m ->> 'maxPieceSize' as maxpiecesize,
    m ->> 'rawPower' as rawpower,
    m ->> 'qualityAdjPower' as qualityadjpower,
    m ->> 'isoCode' as isocode,
    m ->> 'region' as region,
    m ->> 'creditScore' as creditscore,
    m ->> 'score' as score,
    m ->> 'scores' as scores,
    m ->> 'freeSpace' as freespace,
    m ->> 'storageDeals' as storagedeals,
    m ->> 'goldenPath' as goldenpath,
    m ->> 'energy' as energy,
    m ->> 'rank' as rank,
    m ->> 'regionRank' as regionrank
from base
