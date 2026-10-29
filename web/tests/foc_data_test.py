# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.1"]
# ///
# ruff: file-ignore[line-too-long] -- compact synthetic SQL fixtures.
"""Small, synthetic checks for the local explorer export. No production writes."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import duckdb

spec = importlib.util.spec_from_file_location(
    "foc", Path(__file__).parents[1] / "scripts/foc.py"
)
foc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foc)


class ExportTests(unittest.TestCase):
    def test_writer_preserves_wide_integers_and_float_precision(self):
        with tempfile.TemporaryDirectory() as folder:
            con = duckdb.connect()
            writer = foc.Writer(con, Path(folder))
            writer.put(
                "value.json",
                '{"atto":12345678901234567890123456789012345678,"value":1.23456789123,"zero":0,"unknown":null}',
            )
            value = json.loads((Path(folder) / "value.json").read_text())
            self.assertEqual(value["atto"], "12345678901234567890123456789012345678")
            self.assertEqual(value["value"], 1.23456789123)
            self.assertEqual(value["zero"], 0)
            self.assertIsNone(value["unknown"])
            con.close()

    def test_payment_series_never_adds_different_native_tokens(self):
        con = duckdb.connect()
        con.execute(
            "create table pay(date date, rail_id int, gross double, stable boolean)"
        )
        con.execute(
            "insert into pay values ('2026-10-01',1,2,true), ('2026-10-01',2,3,true), ('2026-10-01',3,7,false), ('2026-10-03',1,0,true)"
        )
        stable = json.loads(con.execute("select " + foc.daily("true")).fetchone()[0])
        native = json.loads(
            con.execute(
                "select " + foc.daily("rail_id=3", stable_only=False)
            ).fetchone()[0]
        )
        self.assertEqual(stable["v"], [5, 0])
        self.assertEqual(native["v"], [7])
        self.assertEqual(stable["d"], ["2026-10-01", "2026-10-03"])
        con.close()

    def test_source_is_read_only_and_daily_data_stops_at_yesterday(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.duckdb"
            source = duckdb.connect(str(path))
            source.execute("set TimeZone='UTC'")
            for table in foc.TABLES:
                if table.startswith("daily_") or table == "payments":
                    source.execute(
                        f"create table {table} as select current_date as date union all select current_date - 1"
                    )
                else:
                    source.execute(f"create table {table}(id integer)")
            fields = [
                field.strip().split()[0]
                for field in foc.NETWORK_COLUMNS.split(",")
                if field.strip() != "date"
            ]
            source.execute(
                "create table daily_network_metrics as select current_date as date,"
                + ",".join(f"0 as {field}" for field in fields)
            )
            source.execute(
                "insert into daily_network_metrics select * replace (current_date-1 as date) from daily_network_metrics"
            )
            source.close()
            digest = hashlib.sha256(path.read_bytes()).digest()
            result = foc.connect(str(path))
            for table in [
                "network",
                "payments",
                "daily_operator_metrics",
                "daily_provider_quality",
            ]:
                self.assertEqual(
                    result.execute(
                        f"select count(*) from {table} where date >= current_date"
                    ).fetchone()[0],
                    0,
                )
                self.assertEqual(
                    result.execute(f"select count(*) from {table}").fetchone()[0], 1
                )
            result.close()
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), digest)


if __name__ == "__main__":
    unittest.main()
