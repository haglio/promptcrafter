from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptCrafterRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.attributes_text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")

    def test_the_app_module_imports_inside_this_test_so_a_broken_import_fails_it_alone_not_every_tests_collection(self):
        from promptcrafter.app import PromptCrafterWindow  # noqa: PLC0415
        assert callable(PromptCrafterWindow)

    def test_the_schema_module_loads_inside_this_test_so_a_broken_import_fails_it_alone_not_every_tests_collection(self):
        from promptcrafter.schema import schema  # noqa: PLC0415
        assert len(schema.sections) > 0

    def test_docs_cover_pyqt6_desktop(self):
        assert "PyQt6" in self.readme_text
        assert "python -m promptcrafter" in self.readme_text

    def test_repo_has_line_ending_policy(self):
        assert "* text=auto eol=lf" in self.attributes_text
        assert "*.ps1 text eol=crlf" in self.attributes_text


if __name__ == "__main__":
    unittest.main()
