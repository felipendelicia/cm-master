import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/cm-master"


class PackageTests(unittest.TestCase):
    def test_skill_and_reference_links_resolve_in_installable_folder(self):
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(entry.startswith("---\nname: cm-master\n"))
        for document in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((document.parent / target.split("#")[0]).is_file(), f"{document}: {target}")

    def test_demo_produces_reviewable_package_without_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(REPO / "examples/create_demo.py"), "--root", directory],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            brand = Path(directory) / "brands/taller-rio-demo"
            self.assertTrue((brand / "assets/demo.png").is_file())
            state = json.loads((brand / "posts/demo-feed/state.json").read_text())
            self.assertEqual(state["state"], "pending_approval")
            self.assertIsNone(state["approval"])
            self.assertEqual(output["review"]["post"]["network"], "instagram")
            self.assertFalse(output["published"])


if __name__ == "__main__":
    unittest.main()
