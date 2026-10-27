# asset.description = Dealbot pull-to-park checks.

# asset.materialization = custom

# asset.not_null = backup_date
# asset.not_null = backup_cid

from fdp.resources.probelab import load_backups


def pull_checks() -> None:
    load_backups("pull", "raw.probelab_pull_checks")
