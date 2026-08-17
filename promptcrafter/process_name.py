"""What PromptCrafter's process is called in the Windows task list.

Windows takes what it shows about a process from the file it was started from --
the Details tab's name, the Processes tab's description, the icon beside it --
so a plain ``pythonw.exe`` puts PromptCrafter in the task list as one more
anonymous "Python".  That costs nothing until something strands a process, and
then the task list is the only way back and cannot say which row is safe to end.

This process cannot be named on the way in: writing the copy takes the very
interpreter being named.  So each run makes it for the run after, and
``Update-PromptCrafterShortcut.ps1`` points the shortcut at it once it exists.
"""
from __future__ import annotations

import sys

from promptcrafter.paths import icon_path

APP_NAME = "PromptCrafter"
ROLE = "PromptCrafter"


def namer():
    """The one answer to what this app's copy is called and how it describes itself."""
    from app_support.process_identity import ProcessNamer

    return ProcessNamer(APP_NAME, icon=icon_path())


def name_this_process() -> None:
    """Make the copy the shortcut should start through next time.

    Never fatal: a read-only venv or an antivirus hold costs the name in the
    task list and nothing else.
    """
    try:
        namer().prepare_launcher(ROLE)
    except Exception:
        pass


def named_exe_name() -> str:
    """The file name the shortcut script looks for."""
    return namer().exe_name("pythonw.exe", ROLE)


if __name__ == "__main__":  # `python -m promptcrafter.process_name` prints it for the shortcut script
    sys.stdout.write(named_exe_name())
