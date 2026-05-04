import re
import unittest
import zipfile
from pathlib import Path


class GeneratedCfxSmokeTestCase(unittest.TestCase):
    def test_generated_cfx_is_readable_when_present(self):
        output = Path("output")
        files = sorted(output.glob("Mining*_Capa*.cfx"))
        if not files:
            self.skipTest("No hay .cfx generados en output/")

        target = files[0]
        with zipfile.ZipFile(target, "r") as zf:
            names = zf.namelist()
            self.assertTrue(any(name.lower().endswith(".xml") for name in names))
            xml_payloads = [
                zf.read(name).decode("utf-8", errors="replace")
                for name in names
                if name.lower().endswith(".xml")
            ]

        joined = "\n".join(xml_payloads)
        self.assertNotIn("C:\\Users\\", joined)
        self.assertRegex(joined, re.compile(r"symbol=\"[^\"]+\""))


if __name__ == "__main__":
    unittest.main()
