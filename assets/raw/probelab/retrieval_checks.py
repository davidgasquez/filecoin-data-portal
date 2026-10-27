# asset.description = Dealbot IPFS retrievals of its own deals.

# asset.materialization = custom

# asset.not_null = backup_date
# asset.not_null = backup_cid

from fdp.resources.probelab import load_backups


def retrieval_checks() -> None:
    load_backups("retrieval", "raw.probelab_retrieval_checks")
