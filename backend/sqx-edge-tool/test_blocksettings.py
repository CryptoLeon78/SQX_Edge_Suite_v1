import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from core.blocksettings import (
    blocksetting_file,
    blocksetting_trace,
    load_blocksettings_manifest,
    resolve_blocksetting_entry,
)
from core.plan import Mining
from core.project_generator import generate_project
from core.config_loader import ROOT


class BlockSettingsSourceTestCase(unittest.TestCase):
    def test_manifest_indexes_real_sqb_sources(self):
        manifest = load_blocksettings_manifest()
        self.assertEqual(len(manifest["entries"]), 29)
        self.assertEqual(manifest["version"], 2)
        for entry in manifest["entries"]:
            path = blocksetting_file(entry)
            self.assertTrue(path.is_file(), entry["filename"])
            self.assertEqual(entry["sha256Short"], entry["sha256"][:12].upper())
            self.assertGreater(entry["counts"]["activeBlocks"], 0)

    def test_resolves_capa1_by_family_and_timeframe(self):
        intraday = resolve_blocksetting_entry("BS_Volatilidad", timeframe="H1", capa=1)
        higher_tf = resolve_blocksetting_entry("BS_Volatilidad", timeframe="H4", capa=1)
        self.assertEqual(intraday["canonicalId"], "BS_Volatilidad_v6_intraday_v6")
        self.assertEqual(higher_tf["canonicalId"], "BS_Volatilidad_v6")

    def test_resolves_capa2_recommendations_and_manual_override(self):
        h1 = resolve_blocksetting_entry("BS_Tendencia_v6", timeframe="H1", capa=2)
        d1 = resolve_blocksetting_entry("BS_Tendencia_v6", timeframe="D1", capa=2)
        manual = resolve_blocksetting_entry(
            "BS_Tendencia_v6",
            timeframe="H1",
            capa=2,
            blocksetting_capa2="BS_Filtros_v6_D1",
        )
        self.assertEqual(h1["canonicalId"], "BS_Filtros_v6")
        self.assertEqual(d1["canonicalId"], "BS_Filtros_v6_D1")
        self.assertEqual(manual["canonicalId"], "BS_Filtros_v6_D1")
        self.assertEqual(blocksetting_trace(manual)["filename"], "BS_Filtros_v6_D1.sqb")

    def test_generate_project_patches_blocks_from_resolved_sqb(self):
        mining = Mining(num=77, phase=1, asset="XAUUSD", tf="H1", bs="BS_Volatilidad", dir="long")
        expected = resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=1)
        template = ROOT / "templates" / "Capa1_Long.cfx"
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(generate_project(mining, str(template), tmp, capa=1, sqx_db_path=None))
            self.assertIn("BS_Volatilidad_v6_intraday_v6", out_path.name)
            with zipfile.ZipFile(out_path) as zf:
                xml = ET.fromstring(zf.read("Build-Task1.xml"))
        blocks = next((node for node in xml.iter() if node.tag == "Blocks"), None)
        self.assertIsNotNone(blocks)
        active_keys = [
            node.get("key")
            for node in blocks.iter("Block")
            if str(node.get("use")).lower() == "true"
        ]
        self.assertGreaterEqual(len(active_keys), expected["counts"]["activeBlocks"])
        self.assertTrue(set(expected["activeIndicators"][:5]).issubset(set(active_keys)))
        self.assertIn("Indicators.ATR", active_keys)
        self.assertIn("Indicators.HullMovingAverageATRBands", active_keys)

    def test_generate_project_rebuilds_symbol_resources_for_generated_asset(self):
        mining = Mining(num=78, phase=1, asset="USDJPY", tf="H4", bs="BS_Volatilidad", dir="both")
        template = ROOT / "templates" / "Capa1_Long.cfx"
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(generate_project(mining, str(template), tmp, capa=1, sqx_db_path=None))
            with zipfile.ZipFile(out_path) as zf:
                xml = ET.fromstring(zf.read("Build-Task1.xml"))

        charts = xml.findall(".//Setup/Chart")
        self.assertTrue(charts)
        self.assertTrue(all(chart.get("symbol") == "USDJPY" for chart in charts))
        resources = xml.findall(".//Resources/Symbols/Symbol")
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].get("name"), "USDJPY")
        self.assertEqual(resources[0].get("uSymbol"), "USDJPY")
        self.assertEqual(resources[0].get("source"), "0")
        self.assertEqual(resources[0].get("broker"), "-1")
        self.assertEqual(resources[0].get("precision"), "TICK")
        self.assertEqual(resources[0].get("timezone"), "EETUS")
        self.assertEqual(resources[0].get("dateFrom"), "1506902400000")
        instrument_info = resources[0].find("InstrumentInfo")
        self.assertIsNotNone(instrument_info)
        self.assertEqual(instrument_info.get("instrument"), "USDJPY")
        self.assertEqual(instrument_info.get("broker"), "-1")
        self.assertEqual(instrument_info.get("dataType"), "1")
        self.assertEqual(instrument_info.get("description"), "USDJPY")
        self.assertEqual(instrument_info.get("pointValue"), "1000.0")
        self.assertEqual(instrument_info.get("dateFrom"), "0")
        self.assertEqual(instrument_info.get("rows"), "0")
        resource_instruments = xml.findall(".//Resources/Instruments/InstrumentInfo")
        self.assertTrue(resource_instruments)
        self.assertTrue(all(node.get("instrument") == "USDJPY" for node in resource_instruments))
        self.assertNotIn("XAUUSD_darwinex", ET.tostring(xml, encoding="unicode"))
        self.assertNotIn("AUDCAD_darwinex", ET.tostring(xml, encoding="unicode"))

    def test_generate_project_rewrites_capa2_embedded_strategy_symbol_for_generated_asset(self):
        mining = Mining(num=79, phase=2, asset="USDJPY", tf="H4", bs="BS_Volatilidad", dir="both")
        template = ROOT / "templates" / "Capa2_Base.cfx"
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(generate_project(mining, str(template), tmp, capa=2, sqx_db_path=None))
            with zipfile.ZipFile(out_path) as zf:
                xml = ET.fromstring(zf.read("Build-Task1.xml"))

        charts = {chart.get("symbol") for chart in xml.findall(".//Setup/Chart")}
        self.assertEqual(charts, {"USDJPY"})
        embedded_symbols = [node.text for node in xml.findall(".//BackupStrategyTemplate//symbol")]
        self.assertTrue(embedded_symbols)
        self.assertEqual(set(embedded_symbols), {"USDJPY"})
        xml_text = ET.tostring(xml, encoding="unicode")
        self.assertIn("SQXEDGE_TEMPLATE_USDJPY_H4", xml_text)
        self.assertNotIn("AUDCAD_darwinex", xml_text)
        self.assertNotIn("XAUUSD_darwinex", xml_text)


if __name__ == "__main__":
    unittest.main()
