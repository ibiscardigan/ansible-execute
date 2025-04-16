"""Tests for the CLI argument parser."""

import pytest
from ansible_execute.cli import parse_args


def test_env_arg_valid_dev(monkeypatch) -> None:
    """Test parsing of -e dev argument."""
    monkeypatch.setattr("sys.argv", ["prog", "-e", "dev"])
    args = parse_args()
    assert args.env == "dev"


def test_env_arg_valid_staging(monkeypatch) -> None:
    """Test parsing of -e staging argument."""
    monkeypatch.setattr("sys.argv", ["prog", "-e", "staging"])
    args = parse_args()
    assert args.env == "staging"


def test_env_arg_invalid(monkeypatch) -> None:
    """Test that invalid env value raises SystemExit."""
    monkeypatch.setattr("sys.argv", ["prog", "-e", "banana"])
    with pytest.raises(SystemExit):
        parse_args()


def test_env_arg_required(monkeypatch) -> None:
    """Test that missing -e argument raises SystemExit."""
    monkeypatch.setattr("sys.argv", ["prog"])
    with pytest.raises(SystemExit):
        parse_args()
