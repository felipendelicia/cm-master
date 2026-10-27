import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "scripts/install.py"


class InstallTests(unittest.TestCase):
    def test_installs_complete_portable_skill_without_touching_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "skills/cm-master"
            result = subprocess.run([sys.executable, str(INSTALL), "--host", "codex", "--destination", str(destination)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in ["SKILL.md", "scripts/cm.py", "scripts/cm_state.py", "agents/openai.yaml", "references/publishing.md",
                             "requirements.txt", "requirements-media.txt"]:
                self.assertTrue((destination / relative).is_file(), relative)
            self.assertFalse((Path(directory) / ".cm-master").exists())
            check = subprocess.run([sys.executable, str(destination / "scripts/cm.py"), "--help"], capture_output=True)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_existing_installation_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "cm-master"
            destination.mkdir()
            sentinel = destination / "custom.txt"
            sentinel.write_text("keep")
            result = subprocess.run([sys.executable, str(INSTALL), "--host", "claude", "--destination", str(destination)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("existe", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((destination / "SKILL.md").exists())

    def test_dangling_destination_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "cm-master"
            destination.symlink_to(Path(directory) / "absent", target_is_directory=True)
            result = subprocess.run([sys.executable, str(INSTALL), "--host", "claude", "--destination", str(destination)],
                                    capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"existe", result.stderr)
            self.assertFalse((Path(directory) / "absent").exists())


if __name__ == "__main__":
    unittest.main()
