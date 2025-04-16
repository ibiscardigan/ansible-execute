"""Tests for main CLI entrypoint."""

import builtins
from typing import List
from unittest import mock

import pytest
from ansible_execute import main


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
@mock.patch("ansible_execute.executor.subprocess.run")
def test_main_prints_env(mock_run: mock.Mock, env: str) -> None:
    """Test that main prints and runs the correct command."""
    mock_run.return_value = mock.Mock(returncode=0)
    fake_args: List[str] = ["prog", "-e", env]

    with mock.patch("sys.argv", fake_args), mock.patch.object(
        builtins, "print"
    ) as mock_print:
        main.main()

    mock_print.assert_any_call(f"Running smoke test for environment: {env}")
    mock_run.assert_called_once()
