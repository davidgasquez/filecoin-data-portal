import dagster as dg

import fdp.apis.definitions as api_definitions
import fdp.bigquery.definitions as bigquery_definitions
import fdp.datacapstats.definitions as datacapstats_definitions
import fdp.dbt.definitions as dbt_definitions
import fdp.dune.definitions as dune_definitions
import fdp.spacescope.definitions as spacescope_definitions
from fdp.resources import duckdb_io_manager, duckdb_resource

common_resources = {"duckdb": duckdb_resource, "io_manager": duckdb_io_manager}

definitions = dg.Definitions.merge(
    dg.Definitions(resources=common_resources),
    datacapstats_definitions.definitions,
    dbt_definitions.definitions,
    spacescope_definitions.definitions,
    dune_definitions.definitions,
    api_definitions.definitions,
    bigquery_definitions.definitions,
)
