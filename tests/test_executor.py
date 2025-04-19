"""Tests for ansible playbook executor."""

import subprocess
import json
from unittest import mock

import pytest
from ansible_execute.executor import run_ansible_playbook


@mock.patch("subprocess.run")
def test_run_ansible_playbook_success(mock_run: mock.Mock) -> None:
    """Test successful playbook execution."""
    # Arrange: simulate a zero‑exit code
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    # Act
    run_ansible_playbook("dev", "test")

    # Assert
    expected_extra_vars = json.dumps({"nodes": ["dev"]})
    mock_run.assert_called_once_with(
        [
            "ansible-playbook",
            "ansible/playbooks/test.yml",
            "--extra-vars",
            expected_extra_vars,
        ],
        check=True,
    )


@mock.patch(
    "subprocess.run", side_effect=subprocess.CalledProcessError(2, ["ansible-playbook"])
)
def test_run_ansible_playbook_failure(mock_run: mock.Mock) -> None:
    """Test that a non-zero exit code bubbles up as SystemExit."""
    with pytest.raises(SystemExit) as exc:
        run_ansible_playbook("staging", "test")
    assert exc.value.code == 2
    # We still logged the error inside executor (you could capture it via caplog)
    mock_run.assert_called_once()
