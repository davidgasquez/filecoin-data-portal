from fildata.spacescope import historical_power_data


def model(dbt, session):
    dbt.config(materialized="external")

    return historical_power_data(use_cache=False)
