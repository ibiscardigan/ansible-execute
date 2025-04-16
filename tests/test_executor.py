"""Tests for ansible playbook executor."""

import subprocess
from unittest import mock

import pytest
from ansible_execute.executor import run_ansible_playbook


@mock.patch("subprocess.run")
def test_run_ansible_playbook_success(mock_run: mock.Mock) -> None:
    """Test successful playbook execution."""
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    run_ansible_playbook("dev")
    mock_run.assert_called_once_with(
        [
            "ansible-playbook",
            "ansible/playbooks/smoke_test.yml",
            "--extra-vars",
            "nodes=dev",
        ],
        check=True,
    )


@mock.patch(
    "subprocess.run",
    side_effect=subprocess.CalledProcessError(1, cmd="ansible-playbook"),
)
def test_run_ansible_playbook_failure(_mock_run: mock.Mock) -> None:
    """Test failed playbook execution raises SystemExit."""
    with pytest.raises(SystemExit) as exc_info:
        run_ansible_playbook("staging")
    assert exc_info.value.code == 1
