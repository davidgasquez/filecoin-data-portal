# asset.description = Dealbot data storage checks, one row per deal.

# asset.materialization = custom

# asset.not_null = backup_date
# asset.not_null = backup_cid

from fdp.resources.probelab import load_backups


def storage_checks() -> None:
    load_backups("storage", "raw.probelab_storage_checks")
