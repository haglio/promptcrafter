from __future__ import annotations

import logging

from app_support.logging_utils import install_exception_logging


def log_errors_and_keep_running() -> None:
    install_exception_logging(logging.getLogger("promptcrafter"))
