import os

from fdp.targets.r2 import R2Config, purge_cache

purge_cache(
    R2Config(
        access_key_id="unused",
        secret_access_key="unused",
        account_id="unused",
        bucket="filecoindataportal",
        cloudflare_api_token=os.environ["CLOUDFLARE_API_TOKEN"],
        cloudflare_zone_id=os.environ["CLOUDFLARE_ZONE_ID"],
    )
)
