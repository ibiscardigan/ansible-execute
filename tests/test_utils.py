# pylint: disable=protected-access, missing-function-docstring

import io
from unittest.mock import patch
import pathlib

import pytest
import yaml

from ansible_execute.utils import Config
from ansible_execute import exceptions

SCHEMA_PKG = "ansible_execute.schemas"


def read_fixture(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def test_valid_config_loads(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_valid.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_valid.yml")
        )
        cfg = Config(config_path=config_path, schema_name="schema_valid.yml")
        assert cfg.config_data["section"]["key"] == "value"


def test_missing_required_key_raises(tmp_path):
    config_path = tmp_path / "missing_key.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_missing_key.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_valid.yml")
        )
        with pytest.raises(
            exceptions.ConfigError, match="Missing required key: 'section'"
        ):
            Config(config_path=config_path, schema_name="schema_valid.yml")


def test_wrong_type_in_config_raises(tmp_path):
    config_path = tmp_path / "wrong_type.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_wrong_type.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_valid.yml")
        )
        with pytest.raises(exceptions.ConfigError, match="should be of type str"):
            Config(config_path=config_path, schema_name="schema_valid.yml")


def test_bad_yaml_in_config_raises(tmp_path):
    config_path = tmp_path / "bad_yaml.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_bad_yaml.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_valid.yml")
        )
        with pytest.raises(exceptions.ConfigError, match="Invalid YAML"):
            Config(config_path=config_path, schema_name="schema_valid.yml")


def test_bad_yaml_in_schema_raises(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_valid.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_bad_yaml.yml")
        )
        with pytest.raises(exceptions.ConfigError, match="Could not load schema"):
            Config(config_path=config_path, schema_name="schema_bad_yaml.yml")


def test_schema_not_dict_raises(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_valid.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_invalid_structure.yml")
        )
        with pytest.raises(
            exceptions.ConfigError, match="Top-level schema must be a dictionary"
        ):
            Config(config_path=config_path, schema_name="schema_invalid_structure.yml")


def test_missing_config_file_raises(tmp_path):
    config_path = tmp_path / "missing.yml"

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            read_fixture("tests/fixtures/schema_valid.yml")
        )
        with pytest.raises(exceptions.ConfigError, match="No config file found"):
            Config(config_path=config_path, schema_name="schema_valid.yml")


def test_missing_schema_file_raises(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text(read_fixture("tests/fixtures/config_valid.yml"))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()
        with pytest.raises(exceptions.ConfigError, match="Could not load schema"):
            Config(config_path=config_path, schema_name="schema_missing.yml")


def test_resolve_type_unknown_raises(tmp_path):
    config_path = tmp_path / "valid.yml"
    config_path.write_text("key: value")

    schema = {"key": {"type": "notatype", "mandatory": True}}

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        with pytest.raises(exceptions.ConfigError, match="Unknown type 'notatype'"):
            Config(config_path=config_path, schema_name="dummy.yml")


def test_supported_types_roundtrip(tmp_path):
    values = {
        "str": "abc",
        "int": 1,
        "float": 1.1,
        "bool": True,
        "list": [],
        "dict": {},
    }

    for typename, value in values.items():
        config_path = tmp_path / f"{typename}.yml"
        config_path.write_text(yaml.dump({"val": value}))

        schema = {"val": {"type": typename, "mandatory": True}}

        with patch("ansible_execute.utils.resources.files") as m:
            m.return_value.joinpath.return_value.open.return_value = io.StringIO(
                yaml.dump(schema)
            )
            cfg = Config(config_path=config_path, schema_name="schema.yml")
            assert "val" in cfg.config_data
