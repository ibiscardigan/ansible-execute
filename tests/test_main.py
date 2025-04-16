"""Tests for main CLI entrypoint."""

import builtins
from typing import List
from unittest import mock

import pytest
from ansible_execute import main


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
def test_main_prints_env(env: str) -> None:
    """Test that main prints the selected environment."""
    fake_args: List[str] = ["prog", "-e", env]

    with mock.patch("sys.argv", fake_args), mock.patch.object(
        builtins, "print"
    ) as mock_print:
        main.main()
        mock_print.assert_called_once_with(f"Environment selected: {env}")
