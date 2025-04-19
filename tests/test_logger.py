# pylint: disable=protected-access, missing-function-docstring

import logging
import json
import time
import pytest

from ansible_execute import logger


def teardown_function():
    """
    After each test, remove any handlers from the root logger
    so tests don’t bleed into each other.
    """
    root = logging.getLogger()
    root.handlers.clear()


def test_verbosity_to_level():
    # 0 → WARNING
    assert logger._verbosity_to_level(0) == logging.WARNING
    # 1 → INFO
    assert logger._verbosity_to_level(1) == logging.INFO
    # 2 → DEBUG
    assert logger._verbosity_to_level(2) == logging.DEBUG
    # 3 (and above) → DEBUG
    assert logger._verbosity_to_level(3) == logging.DEBUG
    assert logger._verbosity_to_level(10) == logging.DEBUG


def test_jsonformatter_format_basic():
    # Create a record with known attributes
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="/some/path/app.py",
        lineno=123,
        msg="Failed to process %s",
        args=("item",),
        exc_info=None,
        func="process_item",
    )
    # Override the timestamp for a deterministic test
    fixed_ts = 1_600_000_000.0
    record.created = fixed_ts

    fmt = logger.JSONFormatter()
    out = fmt.format(record)
    data = json.loads(out)

    # Compute expected timestamp string
    expected_ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(fixed_ts))
    assert data["timestamp"] == expected_ts
    assert data["level"] == record.levelname
    # filename is the basename of pathname
    assert data["filename"] == "app.py"
    assert data["func"] == "process_item"
    assert data["line"] == 123
    # getMessage should have applied the arg
    assert data["message"] == "Failed to process item"


def test_configure_logging_interactive_only_console():
    root = logging.getLogger()
    root.handlers.clear()

    # Default: interactive, console enabled, no directory → only StreamHandler
    logger.configure_logging(verbosity=1)

    assert root.level == logging.INFO
    handlers = root.handlers
    assert len(handlers) == 1

    h = handlers[0]
    assert isinstance(h, logging.StreamHandler)
    assert h.level == logging.INFO
    assert isinstance(h.formatter, logger.JSONFormatter)


def test_configure_logging_disable_console():
    root = logging.getLogger()
    root.handlers.clear()

    # Console disabled explicitly
    logger.configure_logging(verbosity=2, enable_console=False)

    assert root.level == logging.DEBUG
    # No handlers at all
    assert root.handlers == []


def test_configure_logging_non_interactive_without_directory_raises():
    root = logging.getLogger()
    root.handlers.clear()

    with pytest.raises(ValueError) as exc:
        logger.configure_logging(verbosity=0, non_interactive=True)
    assert "log directory must be provided" in str(exc.value)


def test_configure_logging_file_logging(tmp_path):
    root = logging.getLogger()
    root.handlers.clear()

    log_dir = tmp_path / "logs"  # doesn't exist yet
    # non_interactive forces file logging, console suppressed
    logger.configure_logging(verbosity=2, log_directory=log_dir, non_interactive=True)

    assert root.level == logging.DEBUG

    # Exactly one FileHandler
    handlers = root.handlers
    assert len(handlers) == 1
    h = handlers[0]
    assert isinstance(h, logging.FileHandler)
    assert h.level == logging.DEBUG

    # Directory should have been created
    assert log_dir.exists() and log_dir.is_dir()

    # Exactly one log file with the correct suffix
    files = list(log_dir.iterdir())
    assert len(files) == 1
    name = files[0].name
    assert name.endswith("_ansible-execute.log")
    assert files[0].stat().st_size == 0 or files[0].stat().st_size >= 0  # file exists


def test_configure_logging_with_console_and_file(tmp_path):
    root = logging.getLogger()
    root.handlers.clear()

    log_dir = tmp_path / "out"
    # interactive + dir given + console enabled → both handlers
    logger.configure_logging(
        verbosity=0, log_directory=log_dir, non_interactive=False, enable_console=True
    )

    assert root.level == logging.WARNING

    types = {type(h) for h in root.handlers}
    assert logging.StreamHandler in types
    assert logging.FileHandler in types

    # File side-effects
    files = list(log_dir.iterdir())
    assert len(files) == 1
    assert files[0].name.endswith("_ansible-execute.log")
