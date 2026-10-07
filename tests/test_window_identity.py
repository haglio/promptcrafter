"""The window has to carry PromptCrafter's own mark and taskbar identity.

Neither comes from the shortcut that launched it.  Qt gives a window no icon
unless it is handed one, so PromptCrafter came up under a generic fallback --
not Python's mark, just what Windows reaches for when an app supplies nothing.
And a process that does not claim the AppUserModelID its pinned shortcut
carries is treated as a different application, so its window opens beside the
pin instead of in it.

Asserted on the entry point's syntax tree as well as on the helpers, because
both calls have to happen before the first window exists: correct helpers that
the entry point never reaches leave the app looking exactly as broken.  The
tree rather than the text, so a line wrap cannot turn this red with the launch
unchanged.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from shared_ui.preview import Preview

from promptcrafter.paths import icon_path, project_root
from promptcrafter.win32 import APP_USER_MODEL_ID, claim_this_checkouts_identity

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY_POINT = ast.parse((REPO_ROOT / "promptcrafter" / "__main__.py").read_text(encoding="utf-8"))


def _calls() -> list[str]:
    """Every call the entry point makes, as it is spelled, in source order."""
    return [ast.unparse(node.func) for node in ast.walk(ENTRY_POINT) if isinstance(node, ast.Call)]


def _first_line_calling(name: str) -> int:
    return min(node.lineno for node in ast.walk(ENTRY_POINT)
               if isinstance(node, ast.Call) and ast.unparse(node.func).endswith(name))


class IconTests(unittest.TestCase):
    def test_the_icon_ships_with_the_checkout(self):
        self.assertTrue(icon_path().is_file(), f"no icon at {icon_path()}")

    def test_the_icon_is_found_in_this_checkout_not_another(self):
        # A worktree has its own copy; resolving to the primary's would judge
        # the wrong file and hide a change made here.
        self.assertEqual(icon_path().parent, project_root())
        self.assertEqual(project_root(), REPO_ROOT)

    def test_the_entry_point_gives_the_icon_to_the_application(self):
        calls = _calls()
        self.assertIn("app.setWindowIcon", calls)
        self.assertIn("icon_path", calls)


def _the_call(name: str) -> ast.Call:
    calls = [node for node in ast.walk(ENTRY_POINT)
             if isinstance(node, ast.Call) and ast.unparse(node.func) == name]
    assert len(calls) == 1, f"the entry point calls {name} {len(calls)} times"
    return calls[0]


class PreviewTests(unittest.TestCase):
    def test_the_entry_point_claims_what_this_checkout_runs_as(self):
        self.assertEqual(ast.unparse(_the_call("claim_this_checkouts_identity")),
                         "claim_this_checkouts_identity(project_root())")

    def test_a_preview_claims_a_taskbar_button_of_its_own(self):
        with patch("promptcrafter.win32.preview_of", return_value=Preview(feature=None)), \
             patch("promptcrafter.win32.sys.platform", "win32"), \
             patch("promptcrafter.win32.claim_taskbar_identity") as claimed:
            shown = claim_this_checkouts_identity(project_root())

        self.assertEqual(shown, Preview(feature=None))
        claimed.assert_called_once_with(f"{APP_USER_MODEL_ID}.Preview")

    def test_the_live_app_claims_the_identity_its_pin_carries(self):
        with patch("promptcrafter.win32.preview_of", return_value=None), \
             patch("promptcrafter.win32.sys.platform", "win32"), \
             patch("promptcrafter.win32.claim_taskbar_identity") as claimed:
            shown = claim_this_checkouts_identity(project_root())

        self.assertIsNone(shown)
        claimed.assert_called_once_with(APP_USER_MODEL_ID)

    def test_a_preview_wears_its_letter_in_the_preview_ink(self):
        self.assertEqual(ast.unparse(_the_call("app.setWindowIcon")),
                         "app.setWindowIcon(app_icon(icon, preview))")

    def test_the_window_is_told_whether_it_is_a_preview(self):
        self.assertEqual(ast.unparse(_the_call("PromptCrafterWindow")),
                         "PromptCrafterWindow(schema, preview=preview)")


class TaskbarIdentityTests(unittest.TestCase):
    def test_the_entry_point_claims_it_before_opening_a_window(self):
        self.assertIn("claim_this_checkouts_identity", _calls())
        self.assertLess(
            _first_line_calling("claim_this_checkouts_identity"), _first_line_calling("QApplication"),
            "the id has to be claimed before the first window exists")

    def test_setting_it_never_takes_the_app_down(self):
        # An app that cannot group its taskbar button is still an app that runs.
        with patch("promptcrafter.win32.sys.platform", "win32"), \
             patch("promptcrafter.win32.claim_taskbar_identity", side_effect=OSError("refused")):
            claim_this_checkouts_identity(project_root())


if __name__ == "__main__":
    unittest.main()
