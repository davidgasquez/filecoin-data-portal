# asset.description = Solstice SRA/SWA deployment parameters pinned to a release commit.

# asset.materialization = dataframe

# asset.column = chain_id | Filecoin EVM chain id.
# asset.column = sra_address | ServiceRewardsActor proxy address.
# asset.column = swa_address | StreamWeightActor proxy address.
# asset.column = initial_orchestrator | Orchestrator seated at SRA initialization.
# asset.column = initial_orchestrator_wallet | Initial orchestrator payout wallet.
# asset.column = activation_epoch | First epoch of quarter 1.
# asset.column = epochs_per_quarter | Quarter length, in epochs.
# asset.column = post_period | Volume posting window, in epochs.
# asset.column = verification_window | Volume verification window, in epochs.
# asset.column = hold_epochs | Governance upgrade hold, in epochs.
# asset.column = source_version | Solstice commit the parameters were read from.
# asset.column = source_url | Upstream deployments.json URL.
# asset.column = fetched_at | Timestamp when this snapshot was fetched.

# asset.not_null = activation_epoch
# asset.not_null = epochs_per_quarter
# asset.unique = chain_id

import datetime as dt

import httpx
import polars as pl

COMMIT = "b9a63a87b5adee272c16d7e507cc9c127fb34f0f"  # v1.0.2, verified on mainnet
URL = (
    "https://raw.githubusercontent.com/filecoin-project/solstice/"
    f"{COMMIT}/deployments.json"
)


def deployments() -> pl.DataFrame:
    response = httpx.get(URL, follow_redirects=True, timeout=30).raise_for_status()
    chain = response.json()["314"]
    return pl.DataFrame(
        [
            {
                "chain_id": 314,
                "sra_address": chain["sra"].lower(),
                "swa_address": chain["swa"].lower(),
                "initial_orchestrator": chain["initialOrchestrator"].lower(),
                "initial_orchestrator_wallet": chain[
                    "initialOrchestratorWallet"
                ].lower(),
                "activation_epoch": chain["activationEpoch"],
                "epochs_per_quarter": chain["epochsPerQuarter"],
                "post_period": chain["postPeriod"],
                "verification_window": chain["verificationWindow"],
                "hold_epochs": chain["hold"],
                "source_version": COMMIT,
                "source_url": URL,
                "fetched_at": dt.datetime.now(dt.UTC).replace(tzinfo=None),
            }
        ],
        schema_overrides={
            "chain_id": pl.Int64,
            "activation_epoch": pl.Int64,
            "epochs_per_quarter": pl.Int64,
        },
    )
