"""Structured logging setup for ansible-execute CLI."""

import logging
import pathlib
import json
import time
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for Vector or other structured log systems."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(record.created)
            ),
            "level": record.levelname,
            "filename": record.filename,
            "func": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)


def configure_logging(
    verbosity: int,
    log_directory: Optional[pathlib.Path] = None,
    non_interactive: bool = False,
    enable_console: bool = True,
) -> None:
    """
    Configure structured JSON logging to stdout and optional log file.

    Args:
        verbosity: Verbosity level from CLI (-v, -vv, -vvv).
        log_directory: Path to log directory (required for non-interactive mode).
        non_interactive: Whether to suppress console output and force file logging.
        enable_console: If False, disables console output even in interactive mode.
    """
    level = _verbosity_to_level(verbosity)
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = JSONFormatter()

    # Console logging
    if not non_interactive and enable_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    # File logging is required in non-interactive mode
    if non_interactive and not log_directory:
        raise ValueError("In non-interactive mode, a log directory must be provided.")

    if log_directory:
        log_directory.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_filename = f"{date_str}_ansible-execute.log"
        log_path = log_directory / log_filename

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)


def _verbosity_to_level(verbosity: int) -> int:
    """
    Map -v/-vv/-vvv to logging levels.

    Args:
        verbosity: Count of -v flags.

    Returns:
        Logging level.
    """
    if verbosity >= 2:
        return logging.DEBUG
    if verbosity == 1:
        return logging.INFO
    return logging.WARNING
