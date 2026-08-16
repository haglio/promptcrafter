import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


class PromptCrafterLauncherContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shortcut_script = (SCRIPTS_DIR / "Update-PromptCrafterShortcut.ps1").read_text(encoding="utf-8")
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.attributes_text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")

    def test_shortcut_points_at_pythonw(self):
        self.assertIn("pythonw", self.shortcut_script)
        self.assertIn("$LauncherArgs = '-m promptcrafter'", self.shortcut_script)
        self.assertIn("Local.PromptCrafter", self.shortcut_script)

    def test_shortcut_points_at_this_projects_own_interpreter(self):
        """Windows works out what a running process IS by matching it against a
        pinned shortcut with the same target, and draws that shortcut's icon for
        it.  Aimed at the shared system interpreter, this shortcut lent
        PromptCrafter's mark to every unrelated Python process on the machine --
        so the task list filled with PromptCrafter rows while PromptCrafter had
        not run in months.  An interpreter inside the checkout is claimed by this
        app and nothing else."""
        self.assertIn(
            r"$LauncherExe = Join-Path $LauncherRoot '.venv\Scripts\pythonw.exe'",
            self.shortcut_script)
        self.assertNotIn("(Get-Command pythonw).Source", self.shortcut_script)

    def test_app_module_imports_cleanly(self):
        from promptcrafter.app import PromptCrafterWindow
        self.assertTrue(callable(PromptCrafterWindow))

    def test_schema_module_loads(self):
        from promptcrafter.schema import schema
        self.assertGreater(len(schema.sections), 0)

    def test_entry_point_exists(self):
        main_file = REPO_ROOT / "promptcrafter" / "__main__.py"
        self.assertTrue(main_file.exists())
        text = main_file.read_text(encoding="utf-8")
        self.assertIn("PromptCrafterWindow", text)
        self.assertIn("QApplication", text)

    def test_docs_cover_pyqt6_desktop(self):
        self.assertIn("PyQt6", self.readme_text)
        self.assertIn("python -m promptcrafter", self.readme_text)

    def test_repo_has_line_ending_policy(self):
        self.assertIn("* text=auto eol=lf", self.attributes_text)
        self.assertIn("*.ps1 text eol=crlf", self.attributes_text)


if __name__ == "__main__":
    unittest.main()
