from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pytest
from app_support.launcher import assert_launchers_match_their_specs, dry_run, launchers

from promptcrafter.process_name import ROLE, namer

REPO_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = REPO_ROOT / "launch_promptcrafter.vbs"
PREVIEW_LAUNCHER = REPO_ROOT / "launch_preview_branch.vbs"


class PromptCrafterLauncherContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.attributes_text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")

    def test_app_module_imports_cleanly(self):
        # Local: importing it here is the whole test, so a module that stops
        # importing fails this rather than the collection of every test.
        from promptcrafter.app import PromptCrafterWindow  # noqa: PLC0415
        self.assertTrue(callable(PromptCrafterWindow))

    def test_schema_module_loads(self):
        # Local, for the same reason as above: the import is the test.
        from promptcrafter.schema import schema  # noqa: PLC0415
        self.assertGreater(len(schema.sections), 0)

    def test_docs_cover_pyqt6_desktop(self):
        self.assertIn("PyQt6", self.readme_text)
        self.assertIn("python -m promptcrafter", self.readme_text)

    def test_repo_has_line_ending_policy(self):
        self.assertIn("* text=auto eol=lf", self.attributes_text)
        self.assertIn("*.ps1 text eol=crlf", self.attributes_text)


def test_the_launchers_are_what_their_specs_render():
    assert_launchers_match_their_specs(REPO_ROOT)


def test_it_starts_through_the_copy_the_app_names_for_itself():
    """The app makes that copy for the run after (``promptcrafter.process_name``),
    and only a launcher asking for it by the same name starts through it."""
    (launcher,) = [found for found in launchers(REPO_ROOT) if found.file == LAUNCHER.name]

    assert (launcher.interpreter, launcher.named_interpreter) == (
        "pythonw.exe", namer().exe_name("pythonw.exe", ROLE))


@pytest.mark.skipif(sys.platform != "win32", reason="the Windows script host")
def test_it_runs_the_package_from_this_checkout_on_its_own_venv():
    """The working directory is what makes the repo's own ``promptcrafter``
    package resolve rather than an installed or sibling one."""
    report = dry_run(LAUNCHER)

    assert Path(report.value("interpreter")).parent == REPO_ROOT / ".venv" / "Scripts"
    assert Path(report.value("directory")) == REPO_ROOT
    assert report.value("arguments") == "-m promptcrafter"


@pytest.mark.skipif(sys.platform != "win32", reason="the Windows script host")
def test_a_preview_runs_this_worktree_on_the_primary_checkouts_venv():
    """The working directory is what makes ``-m promptcrafter`` resolve to the
    branch's code rather than to the editable install, which names the primary:
    started anywhere else the preview comes up on main, looking like the branch."""
    report = dry_run(PREVIEW_LAUNCHER)

    primary = REPO_ROOT.parents[2]
    assert Path(report.value("interpreter")) == primary / ".venv" / "Scripts" / "pythonw.exe"
    assert Path(report.value("directory")) == REPO_ROOT
    assert report.value("arguments") == "-m promptcrafter"
    assert Path(report.value("log")) == REPO_ROOT / "promptcrafter-preview-launcher.log"


if __name__ == "__main__":
    unittest.main()
