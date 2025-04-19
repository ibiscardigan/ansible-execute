# pylint: disable=missing-function-docstring,wrong-import-order,unused-import,missing-class-docstring

import sys
import logging
from unittest import mock
from types import SimpleNamespace

import pytest

from ansible_execute.main import main
from ansible_execute import utils, cli


class FakeConfig:
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        # Provide a config_data dict so main() can do .get(...) without errors
        self.config_data = {}


@pytest.fixture(autouse=True)
def disable_side_effects(monkeypatch):
    # Stub out structured‐logging setup to at least set INFO level
    monkeypatch.setattr(
        "ansible_execute.logger.configure_logging",
        lambda *args, **kwargs: logging.getLogger().setLevel(logging.INFO),
    )
    # Stub out Config to avoid file I/O
    monkeypatch.setattr(utils, "Config", FakeConfig)


def test_main_generates_config(tmp_path, monkeypatch):
    # Arrange: simulate --generate-config
    output = tmp_path / "out.yml"
    args = SimpleNamespace(
        config=None,
        generate_config=output,
        validate_config=None,
        verbose=1,
        non_interactive=False,
        env=None,
        test=False,
    )
    monkeypatch.setattr(cli, "parse_args", lambda: args)

    # Spy on ConfigGenerator.generate
    fake_gen = type("FakeGen", (), {})()
    called = {}

    def fake_generate(output_path):
        called["output_path"] = output_path

    fake_gen.generate = fake_generate
    monkeypatch.setattr(utils, "ConfigGenerator", lambda: fake_gen)

    # Act
    main()

    # Assert
    assert called["output_path"] == output


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
@mock.patch("ansible_execute.executor.subprocess.run")
def test_main_runs_playbook_in_normal_mode(mock_run, env, caplog):
    """
    When not in test mode, main() should call subprocess.run and log the
    playbook start, the smoke test message, and success.
    """
    # Arrange
    mock_run.return_value = mock.Mock(returncode=0)
    sys.argv[:] = ["prog", "-e", env]

    # Capture INFO logs
    caplog.set_level(logging.INFO)

    # Act
    main()

    # Assert: playbook was invoked
    mock_run.assert_called_once()
    # Assert: main() logged it
    assert "Running Ansible playbook..." in caplog.text
    # Assert: executor logged start of smoke test
    assert f"Starting execution for environment: {env}" in caplog.text
    # Assert: executor logged success
    assert "Playbook executed successfully" in caplog.text


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
@mock.patch("ansible_execute.executor.subprocess.run")
def test_main_skips_playbook_in_test_mode(mock_run, env, caplog):
    """
    When in test mode (-t), main() should NOT call subprocess.run and should
    log the skip message.
    """
    # Arrange
    sys.argv[:] = ["prog", "-e", env, "-t"]

    # Capture INFO logs
    caplog.set_level(logging.INFO)

    # Act
    main()

    # Assert: no playbook invocation
    mock_run.assert_not_called()
    # Assert: skip message
    assert f"Test mode enabled, skipping playbook execution for {env}." in caplog.text


def test_main_validates_config(monkeypatch, tmp_path, caplog):
    """
    When --validate-config is used, main() should log validation success.
    """
    # Arrange: create a dummy config file
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text("foo: bar")
    args = SimpleNamespace(
        config=cfg_file,
        generate_config=None,
        validate_config=True,
        verbose=1,
        non_interactive=False,
        env=None,
        test=False,
    )
    monkeypatch.setattr(cli, "parse_args", lambda: args)

    # Capture INFO logs
    caplog.set_level(logging.INFO)

    # Act
    main()

    # Assert
    assert "Configuration is valid." in caplog.text
