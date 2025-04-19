"""Config validation and generation for ansible-execute."""

import pathlib
from importlib import resources

import yaml

from ansible_execute import exceptions

SCHEMA_PACKAGE = "ansible_execute.schemas"


class Config:
    """Loads and validates a config file against a defined schema."""

    def __init__(
        self, config_path: pathlib.Path, schema_name: str = "default_config.yml"
    ) -> None:
        """
        Initialize and validate a config file against a bundled schema.

        Args:
            config_path: Path to the user-provided config as pathlib.Path.
            schema_name: Bundled schema name used for validation.
        """
        self.config_path: pathlib.Path = config_path

        # Load schema definition from package
        try:
            with resources.files(SCHEMA_PACKAGE).joinpath(schema_name).open(
                "r", encoding="utf-8"
            ) as f:
                self.schema_def: dict = yaml.safe_load(f)
        except (yaml.YAMLError, FileNotFoundError, OSError) as exc:
            raise exceptions.ConfigError(
                f"[Config] Could not load schema '{schema_name}' from bundled package"
            ) from exc

        if not isinstance(self.schema_def, dict):
            raise exceptions.ConfigError(
                "[Config] Top-level schema must be a dictionary"
            )

        if not self.config_path.is_file():
            raise exceptions.ConfigError(
                f"[Config] No config file found at {self.config_path}"
            )

        # Load and parse config file
        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                self.config_data: dict = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as exc:
            raise exceptions.ConfigError(
                f"[Config] Invalid YAML in {self.config_path}"
            ) from exc

        if not isinstance(self.config_data, dict):
            raise exceptions.ConfigError(
                "[Config] Top-level config must be a dictionary"
            )

        # Validate config
        self.validate_config_against_schema(self.config_data, self.schema_def)

    def validate_config_against_schema(
        self, config: dict, schema: dict, path: str = ""
    ) -> None:
        """
        Recursively validate the config against the expected schema.

        Args:
            config: Actual loaded config.
            schema: Expected schema.
            path: Dot-path used for error context.
        """
        for key in config:
            if key not in schema:
                full_path = f"{path}.{key}" if path else key
                raise exceptions.ConfigError(f"[Config] Unexpected key: '{full_path}'")

        for key, rules in schema.items():
            full_path = f"{path}.{key}" if path else key

            if rules.get("mandatory", False) and key not in config:
                raise exceptions.ConfigError(
                    f"[Config] Missing required key: '{full_path}'"
                )

            if key not in config:
                continue  # optional and not provided

            value = config[key]
            expected_type = rules.get("type")
            python_type = self._resolve_type(expected_type)

            if python_type is dict:
                if not isinstance(value, dict):
                    raise exceptions.ConfigError(
                        f"[Config] Key '{full_path}' should be a dict"
                    )
                self.validate_config_against_schema(
                    value, rules.get("children", {}), path=full_path
                )
            elif python_type is list:
                if not isinstance(value, list):
                    raise exceptions.ConfigError(
                        f"[Config] Key '{full_path}' should be a list"
                    )
                # Optional: validate list elements here
            else:
                if not isinstance(value, python_type):
                    raise exceptions.ConfigError(
                        f"[Config] Key '{full_path}' should be of type {python_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

    def _resolve_type(self, type_name: str) -> type:
        """
        Convert string type names from schema to native Python types.
        """
        mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
        }
        if type_name not in mapping:
            raise exceptions.ConfigError(
                f"[Config] Unknown type '{type_name}' in schema"
            )
        return mapping[type_name]


class ConfigGenerator:
    """Generates a default config YAML from a bundled schema definition."""

    def __init__(self, schema_name: str = "default_config.yml") -> None:
        """
        Initialize the config generator by loading a bundled schema.

        Args:
            schema_name: Name of the schema file inside the bundled package.
        """
        try:
            with resources.files(SCHEMA_PACKAGE).joinpath(schema_name).open(
                "r", encoding="utf-8"
            ) as f:
                self.schema_def: dict = yaml.safe_load(f)
        except (yaml.YAMLError, FileNotFoundError, OSError) as exc:
            raise exceptions.ConfigError(
                f"[ConfigGenerator] Could not load schema '{schema_name}' from bundled package"
            ) from exc

        if not isinstance(self.schema_def, dict):
            raise exceptions.ConfigError(
                "[ConfigGenerator] Top-level schema must be a dictionary"
            )

    def generate(
        self, output_path: pathlib.Path = pathlib.Path("config.generated.yml")
    ) -> None:
        """
        Generate a default config file in the current working directory.

        Args:
            output_path: Path to write the generated config file.
        """
        config = self._extract_defaults_from_schema(self.schema_def)
        out_path = pathlib.Path.cwd() / output_path

        with out_path.open("w", encoding="utf-8") as f:
            yaml.dump(config, f, sort_keys=False)

        print(f"Default config written to {out_path}")

    def _extract_defaults_from_schema(self, schema: dict) -> dict:
        """
        Recursively build config from schema defaults.

        Args:
            schema: Parsed schema dict.

        Returns:
            dict: Configuration with default values.
        """
        config: dict = {}

        for key, rules in schema.items():
            expected_type = rules.get("type")
            default = rules.get("default")

            if expected_type == "dict":
                config[key] = self._extract_defaults_from_schema(
                    rules.get("children", {})
                )
            elif expected_type == "list":
                config[key] = default if default is not None else []
            else:
                config[key] = default if default is not None else ""

        return config
