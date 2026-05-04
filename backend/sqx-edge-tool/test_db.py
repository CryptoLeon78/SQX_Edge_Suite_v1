import unittest
from pathlib import Path

from api.server import load_config
from core.plan import all_minings, get as get_mining
from core.project_generator import DEFAULT_BROKER_POSTFIX, resolve_costs


class DbCostResolutionTestCase(unittest.TestCase):
    def test_resolve_costs_uses_configured_aliases_when_db_exists(self):
        cfg = load_config()
        db_path = cfg.get("sqx_data_db")
        if not db_path or not Path(db_path).is_file():
            self.skipTest("SQX data.db no configurado en este entorno")

        aliases = cfg.get("asset_aliases") or {}
        mining = next((m for m in all_minings() if m.asset in aliases), None)
        if mining is None:
            self.skipTest("config.json no define aliases para activos del plan")

        costs = resolve_costs(
            mining,
            db_path,
            cfg.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX,
            alias_override=aliases,
        )

        self.assertIn("symbol", costs)
        self.assertIn("source", costs)
        self.assertIn("spread", costs)
        self.assertEqual(costs.get("instrument"), aliases[mining.asset])

    def test_resolve_costs_falls_back_without_db(self):
        mining = get_mining(1)
        costs = resolve_costs(mining, None, DEFAULT_BROKER_POSTFIX)

        self.assertEqual(costs["source"], "fallback")
        self.assertTrue(costs["symbol"].startswith(mining.asset))
        self.assertIn("spread", costs)


if __name__ == "__main__":
    unittest.main()
