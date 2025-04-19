# pylint: disable=protected-access, missing-function-docstring

import io
from unittest.mock import patch

import yaml
import pytest

from ansible_execute.utils import Config, ConfigGenerator
from ansible_execute import exceptions


def test_config_not_dict(tmp_path):
    config_path = tmp_path / "list_config.yml"
    config_path.write_text("- not a dict")

    schema = {"x": {"type": "str", "mandatory": True}}

    with patch("ansible_execute.utils.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        with pytest.raises(
            exceptions.ConfigError, match="Top-level config must be a dictionary"
        ):
            Config(config_path=config_path)


def test_list_field_wrong_type(tmp_path):
    schema = {
        "x": {
            "type": "dict",
            "mandatory": True,
            "children": {"tags": {"type": "list", "mandatory": True}},
        }
    }
    config = {"x": {"tags": "notalist"}}
    config_path = tmp_path / "badlist.yml"
    config_path.write_text(yaml.dump(config))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        with pytest.raises(exceptions.ConfigError, match="should be a list"):
            Config(config_path=config_path)


def test_scalar_type_mismatch(tmp_path):
    schema = {"foo": {"type": "int", "mandatory": True}}
    config = {"foo": "notanint"}
    config_path = tmp_path / "badscalar.yml"
    config_path.write_text(yaml.dump(config))

    with patch("ansible_execute.utils.resources.files") as m:
        m.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        with pytest.raises(exceptions.ConfigError, match="should be of type int"):
            Config(config_path=config_path)


def test_config_generator_invalid_yaml():
    with patch("ansible_execute.utils.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open.return_value = io.StringIO(
            "bad: [yaml"
        )
        with pytest.raises(exceptions.ConfigError, match="Could not load schema"):
            ConfigGenerator(schema_name="dummy.yml")


def test_config_generator_not_dict_schema():
    with patch("ansible_execute.utils.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open.return_value = io.StringIO(
            "[1, 2, 3]"
        )
        with pytest.raises(
            exceptions.ConfigError, match="Top-level schema must be a dictionary"
        ):
            ConfigGenerator(schema_name="dummy.yml")


def test_config_generator_output(tmp_path):
    schema = {
        "section": {
            "type": "dict",
            "mandatory": True,
            "children": {
                "key": {"type": "str", "default": "value"},
                "tags": {"type": "list", "default": ["a", "b"]},
            },
        }
    }
    output_path = tmp_path / "out.yml"

    with patch("ansible_execute.utils.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        generator = ConfigGenerator(schema_name="dummy.yml")
        generator.generate(output_path=output_path)

    result = yaml.safe_load(output_path.read_text())
    assert result["section"]["key"] == "value"
    assert result["section"]["tags"] == ["a", "b"]


def test_extract_defaults_full_matrix(tmp_path):
    schema = {
        "everything": {
            "type": "dict",
            "mandatory": True,
            "children": {
                "a": {"type": "str", "default": "abc"},
                "b": {"type": "int", "default": 1},
                "c": {"type": "float", "default": 3.14},
                "d": {"type": "bool", "default": True},
                "e": {"type": "list"},
                "f": {"type": "dict"},
                "g": {
                    "type": "dict",
                    "children": {"inner": {"type": "str", "default": "nested"}},
                },
            },
        }
    }
    output_path = tmp_path / "matrix.yml"

    with patch("ansible_execute.utils.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open.return_value = io.StringIO(
            yaml.dump(schema)
        )
        generator = ConfigGenerator(schema_name="dummy.yml")
        generator.generate(output_path=output_path)

    data = yaml.safe_load(output_path.read_text())
    assert data["everything"]["a"] == "abc"
    assert data["everything"]["b"] == 1
    assert data["everything"]["c"] == 3.14
    assert data["everything"]["d"] is True
    assert data["everything"]["e"] == []
    assert data["everything"]["f"] == {}
    assert data["everything"]["g"]["inner"] == "nested"
