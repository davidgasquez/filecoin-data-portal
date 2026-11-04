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

    def test_orchestrator_activity_separates_tokens_and_counts_distinct_payers(self):
        con = duckdb.connect()
        con.execute("set TimeZone='UTC'")
        con.execute(
            "create table rails(token varchar, token_symbol varchar, token_decimals int)"
        )
        con.execute("insert into rails values ('usdc','USDC',6), ('usdc','USDC',6)")
        con.execute(
            "create table orchestrator_settlements(orchestrator varchar, date date, payer varchar, token varchar, amount decimal(38,0))"
        )
        con.execute("""insert into orchestrator_settlements values
            ('a','2026-10-01','p1','usdc',1000001), ('a','2026-10-01','p1','usdc',2000000),
            ('a','2026-10-01','p1','0x0000000000000000000000000000000000000000',1000000000000000001),
            ('a','2026-10-01','p2','usdc',0), ('other','2026-10-01','p3','usdc',9999999),
            ('a','2026-10-03','p2','usdc',4000000)""")
        foc.tokens(con)
        data = json.loads(
            con.execute(
                "select " + foc.orchestrator_activity("orchestrator='a'")
            ).fetchone()[0]
        )
        self.assertEqual([d["payers"] for d in data["daily"]], [1, 1])
        self.assertEqual(len(data["tokens"]), 2)
        fil, usdc = data["tokens"]
        self.assertEqual((fil["symbol"], fil["decimals"]), ("FIL", 18))
        self.assertEqual(str(fil["daily"][0]["amount"]), "1000000000000000001")
        self.assertEqual((usdc["symbol"], usdc["decimals"]), ("USDC", 6))
        self.assertEqual(
            [str(d["amount"]) for d in usdc["daily"]], ["3000001", "4000000"]
        )
        self.assertEqual(len(usdc["daily"]), 2)
        con.close()

    def test_tokens_name_native_fil_and_never_guess_decimals(self):
        con = duckdb.connect()
        con.execute(
            "create table rails as select * from (values ('0x0000000000000000000000000000000000000000', null, null), ('usdc', 'USDC', 6), ('odd', 'ODD', 6), ('odd', 'ODD', 18)) t(token, token_symbol, token_decimals)"
        )
        foc.tokens(con)
        self.assertEqual(
            con.execute("select * from tokens order by token").fetchall(),
            [
                ("0x0000000000000000000000000000000000000000", "FIL", 18),
                ("odd", "ODD", None),
                ("usdc", "USDC", 6),
            ],
        )
        con.execute("delete from rails where token like '0x%'")
        con.execute("drop table tokens")
        foc.tokens(con)
        # FIL settlements need a symbol even without a native rail.
        self.assertEqual(
            con.execute(
                "select symbol, decimals from tokens where token like '0x%'"
            ).fetchone(),
            ("FIL", 18),
        )
        con.close()

    def entity_fixture(self, handoffs=0):
        con = duckdb.connect()
        con.execute("set TimeZone='UTC'")
        con.execute("""create table checkpoints as select d::date as date from
            generate_series(date '2026-01-01', date '2026-01-04', interval 1 day) dates(d)""")
        # These are the typed histories on the public entities, not chain-event fixtures.
        con.execute("""create table rails(
            rail_id bigint, payer varchar, token varchar, token_symbol varchar, token_decimals int,
            rate_history struct(date date, rate decimal(38,0))[])""")
        con.execute("""insert into rails values
            (1,'p','usdc','USDC',6,[{date:'2026-01-01',rate:0},{date:'2026-01-02',rate:1000},{date:'2026-01-04',rate:0}]),
            (2,'p','0x0000000000000000000000000000000000000000',null,null,[{date:'2026-01-02',rate:7}]),
            (3,'p','usdc','USDC',6,[{date:'2026-01-02',rate:5}]),
            (4,'q','usdc','USDC',6,[{date:'2026-01-01',rate:0}])""")
        con.execute("""create table data_sets(data_set_id bigint, storage_provider_attribution_safe boolean,
            storage_history struct(date date, pieces bigint, bytes bigint, added bigint, removed bigint)[])""")
        con.execute(f"""insert into data_sets values (70, {not handoffs},
            [{{date:'2026-01-01',pieces:2,bytes:10,added:10,removed:0}},
             {{date:'2026-01-02',pieces:3,bytes:15,added:5,removed:0}},
             {{date:'2026-01-04',pieces:0,bytes:0,added:0,removed:5}}])""")
        con.execute(
            "create table d as select 70 as id, 'p' as owner, 9 as provider_id, 1 as pdp_rail_id"
        )
        foc.tokens(con)
        foc.daily_model(con)
        foc.entity_series(con)
        return con

    def test_entity_series_follow_checkpoints_mapping_and_removals(self):
        con = self.entity_fixture()

        def one(sql):
            return json.loads(con.execute(sql).fetchone()[0])

        storage = one("select j from ds_storage where k = 70")
        self.assertEqual(storage["d"], ["2026-01-01", "2026-01-02", "2026-01-04"])
        self.assertEqual(storage["pieces"], [2, 3, 0])
        self.assertEqual(storage["bytes"], [10, 15, 0])
        self.assertEqual(storage["added"], [10, 5, 0])
        # Deletions end the stored state but are not PiecesRemoved flow.
        self.assertEqual(storage["removed"], [0, 0, 5])
        self.assertEqual(
            con.execute("select count(*) from ds_storage").fetchone()[0], 1
        )
        self.assertEqual(
            one("select j from owner_storage where k = 'p'")["bytes"], [10, 15, 0]
        )
        self.assertEqual(
            one("select j from provider_storage where k = 9")["bytes"], [10, 15, 0]
        )
        con.close()

    def test_rail_rates_change_end_at_zero_and_keep_tokens_apart(self):
        con = self.entity_fixture()

        def one(sql):
            return json.loads(con.execute(sql).fetchone()[0])

        self.assertEqual(
            one("select j from rate_json where k = 1"),
            {"d": ["2026-01-01", "2026-01-02", "2026-01-04"], "v": ["0", "1000", "0"]},
        )
        # A zero-rate rail is a zero state, never a paying day.
        self.assertEqual(
            one("select j from rate_json where k = 4"),
            {"d": ["2026-01-01"], "v": ["0"]},
        )
        self.assertIsNone(
            con.execute("select j from payer_rates where payer = 'q'").fetchone()
        )
        fil, usdc = one("select j from payer_rates where payer = 'p'")
        self.assertEqual(
            (fil["symbol"], fil["decimals"], fil["d"], fil["v"]),
            ("FIL", 18, ["2026-01-02", "2026-01-03", "2026-01-04"], ["7", "7", "7"]),
        )
        self.assertEqual(
            (usdc["symbol"], usdc["decimals"], usdc["d"], usdc["v"]),
            (
                "USDC",
                6,
                ["2026-01-02", "2026-01-03", "2026-01-04"],
                ["1005", "1005", "5"],
            ),
        )
        self.assertEqual(
            one("select j from owner_billing where k = 'p'"),
            {"d": ["2026-01-02", "2026-01-03"], "v": [1, 1]},
        )
        self.assertEqual(
            one("select j from provider_clients where k = 9"),
            {"d": ["2026-01-02", "2026-01-03"], "v": [1, 1]},
        )
        con.close()

    def test_provider_storage_is_withheld_after_handoffs_and_empty_inputs_export_nothing(
        self,
    ):
        con = self.entity_fixture(handoffs=1)
        self.assertEqual(
            con.execute("select count(*) from provider_storage").fetchone()[0], 0
        )
        con.close()
        con = self.entity_fixture()
        # No entity histories is valid and exports no chart series.
        for table in ["data_sets", "rails", "d"]:
            con.execute(f"delete from {table}")
        for table in [
            "ds_delta",
            "rail_rates",
            "rail_days",
            "tokens",
            "rate_json",
            "ds_storage",
            "owner_storage",
            "provider_storage",
            "provider_clients",
            "owner_billing",
            "payer_rates",
        ]:
            con.execute(f"drop table {table}")
        foc.tokens(con)
        foc.daily_model(con)
        foc.entity_series(con)
        for table in [
            "ds_storage",
            "rate_json",
            "payer_rates",
            "owner_billing",
            "provider_clients",
        ]:
            self.assertEqual(
                con.execute(f"select count(*) from {table}").fetchone()[0], 0
            )
        con.close()

    def test_source_is_read_only_and_daily_data_stops_at_yesterday(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.duckdb"
            source = duckdb.connect(str(path))
            source.execute("set TimeZone='UTC'")
            for table in foc.TABLES:
                if table == "rails":
                    source.execute("""create table rails as select current_date - 1 as history_start,
                        current_date as history_end""")
                elif table == "service_orchestrators":
                    source.execute("""create table service_orchestrators as select 'o' as orchestrator,
                        [{date:current_date,payer:'p',token:'t',amount:1::decimal(38,0)},
                         {date:current_date-1,payer:'p',token:'t',amount:2::decimal(38,0)}] as payment_history""")
                elif table.startswith("daily_") or table == "payments":
                    source.execute(
                        f"create table {table} as select current_date as date union all select current_date - 1"
                    )
                else:
                    source.execute(f"create table {table}(id integer)")
            # Deliberately no raw/model schemas: this matches fdp export, unlike the working DB.
            self.assertEqual(
                source.execute(
                    "select distinct schema_name from duckdb_tables()"
                ).fetchall(),
                [("main",)],
            )
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
            self.assertEqual(
                result.execute(
                    "select count(*) from orchestrator_settlements"
                ).fetchone()[0],
                1,
            )
            self.assertEqual(
                result.execute("select count(*) from checkpoints").fetchone()[0], 1
            )
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
