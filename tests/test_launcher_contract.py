import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


class PromptCrafterLauncherContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        cls.build_script = (SCRIPTS_DIR / "Build-PromptCrafterExecutable.ps1").read_text(encoding="utf-8")
        cls.shortcut_script = (SCRIPTS_DIR / "Update-PromptCrafterShortcut.ps1").read_text(encoding="utf-8")
        cls.electron_main = (SCRIPTS_DIR / "electron-main.mjs").read_text(encoding="utf-8")
        cls.electron_preload = (SCRIPTS_DIR / "electron-preload.cjs").read_text(encoding="utf-8")
        cls.readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        cls.attributes_text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
        cls.clipboard_helper = (REPO_ROOT / "src" / "lib" / "clipboard.ts").read_text(encoding="utf-8")
        cls.main_source = (REPO_ROOT / "src" / "main.tsx").read_text(encoding="utf-8")

    def test_package_json_points_to_electron_main(self):
        self.assertEqual(self.package_json["main"], "scripts/electron-main.mjs")
        self.assertEqual(self.package_json["scripts"]["desktop:dev"], "node ./scripts/desktop-dev.mjs")
        self.assertIn("electron", self.package_json["devDependencies"])
        self.assertIn("@electron/packager", self.package_json["devDependencies"])

    def test_build_script_packages_electron_runtime(self):
        self.assertIn("Generate-PromptCrafterIcon.py", self.build_script)
        self.assertIn("npm.cmd", self.build_script)
        self.assertIn("run build", self.build_script)

    def test_shortcut_points_at_electron_dev_shell(self):
        self.assertIn("node_modules\\electron\\dist\\electron.exe", self.shortcut_script)
        self.assertIn("$LauncherArgs = '.'", self.shortcut_script)
        self.assertIn("Alex.PromptCrafter", self.shortcut_script)

    def test_electron_host_has_logging_and_local_server(self):
        self.assertIn("promptcrafter-launcher.log", self.electron_main)
        self.assertIn("startStaticServer", self.electron_main)
        self.assertIn("/__launcher_log__", self.electron_main)
        self.assertIn("BrowserWindow", self.electron_main)
        self.assertIn("PROMPTCRAFTER_DEV_SERVER_URL", self.electron_main)
        self.assertIn("startViteDevServer", self.electron_main)

    def test_electron_preload_exposes_clipboard_bridge(self):
        self.assertIn("promptCrafterDesktop", self.electron_preload)
        self.assertIn("promptcrafter:copy-text", self.electron_preload)
        self.assertIn("copyText(text)", self.electron_preload)

    def test_renderer_has_clipboard_fallback_and_client_diagnostics(self):
        self.assertIn("promptCrafterDesktop?.copyText", self.clipboard_helper)
        self.assertIn("window.addEventListener('error'", self.main_source)
        self.assertIn("window.addEventListener('unhandledrejection'", self.main_source)
        self.assertIn("'dom'", self.main_source)

    def test_docs_cover_electron_desktop_shell(self):
        self.assertIn("Electron", self.readme_text)
        self.assertIn("does not open a browser tab", self.readme_text)
        self.assertIn("live-reload desktop app", self.readme_text)
        self.assertIn("hot reload", self.readme_text)

    def test_repo_has_line_ending_policy(self):
        self.assertIn("* text=auto eol=lf", self.attributes_text)
        self.assertIn("*.ps1 text eol=crlf", self.attributes_text)


if __name__ == "__main__":
    unittest.main()
