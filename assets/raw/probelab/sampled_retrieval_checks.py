# asset.description = Dealbot piece retrievals of sampled non-Dealbot pieces.

# asset.materialization = custom

# asset.not_null = backup_date
# asset.not_null = backup_cid

from fdp.resources.probelab import load_backups


def sampled_retrieval_checks() -> None:
    load_backups("sampled_retrieval", "raw.probelab_sampled_retrieval_checks")
