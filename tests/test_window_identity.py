"""The window has to carry PromptCrafter's own mark and taskbar identity.

Neither comes from the shortcut that launched it.  Qt gives a window no icon
unless it is handed one, so PromptCrafter came up under a generic fallback --
not Python's mark, just what Windows reaches for when an app supplies nothing.
And a process that does not claim the AppUserModelID its pinned shortcut
carries is treated as a different application, so its window opens beside the
pin instead of in it.

Asserted on the entry point's source as well as on the helpers, because both
calls have to happen before the first window exists: correct helpers that the
entry point never reaches leave the app looking exactly as broken.
"""
import unittest
from pathlib import Path

from promptcrafter.paths import icon_path, project_root
from promptcrafter.win32 import APP_USER_MODEL_ID, set_app_user_model_id

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY_POINT = (REPO_ROOT / "promptcrafter" / "__main__.py").read_text(encoding="utf-8")


class IconTests(unittest.TestCase):
    def test_the_icon_ships_with_the_checkout(self):
        self.assertTrue(icon_path().is_file(), f"no icon at {icon_path()}")

    def test_the_icon_is_found_in_this_checkout_not_another(self):
        # A worktree has its own copy; resolving to the primary's would judge
        # the wrong file and hide a change made here.
        self.assertEqual(icon_path().parent, project_root())
        self.assertEqual(project_root(), REPO_ROOT)

    def test_the_entry_point_gives_the_icon_to_the_application(self):
        self.assertIn("setWindowIcon", ENTRY_POINT)
        self.assertIn("icon_path", ENTRY_POINT)


class TaskbarIdentityTests(unittest.TestCase):
    def test_the_id_matches_the_one_the_shortcut_stamps(self):
        script = (REPO_ROOT / "scripts" / "Update-PromptCrafterShortcut.ps1").read_text(encoding="utf-8")
        self.assertIn(f"$AppUserModelId = '{APP_USER_MODEL_ID}'", script)

    def test_the_entry_point_claims_it_before_opening_a_window(self):
        self.assertIn("set_app_user_model_id()", ENTRY_POINT)
        self.assertLess(
            ENTRY_POINT.index("set_app_user_model_id()"), ENTRY_POINT.index("QApplication(sys.argv)"),
            "the id has to be claimed before the first window exists")

    def test_setting_it_never_takes_the_app_down(self):
        # An app that cannot group its taskbar button is still an app that runs.
        set_app_user_model_id("PromptCrafter.Test.Identity")


if __name__ == "__main__":
    unittest.main()
