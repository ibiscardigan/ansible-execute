"""Command-line interface for Ansible execution tool."""

import argparse
import pathlib
from argparse import Namespace


def parse_args() -> Namespace:
    """
    Parse command-line arguments.

    Returns:
        Namespace: Parsed arguments including environment, config, test mode,
                   validation and generation options.
    """
    parser = argparse.ArgumentParser(
        description="Ansible execution CLI for homelab environments"
    )

    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=pathlib.Path("execute_config.yml"),
        help="Path to config file (default: ./execute_config.yml)",
    )

    parser.add_argument(
        "-e",
        "--env",
        default="prod",
        choices=["dev", "staging", "prod"],
        help="Target environment (default: prod)",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run in test mode (does not execute Ansible commands)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v, -vv, -vvv)",
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (console output will be disabled)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--generate-config",
        nargs="?",
        const=pathlib.Path("execute_config.yml"),
        type=pathlib.Path,
        help="Generate a default config at the given path (default: ./execute_config.yml)",
    )
    group.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate the provided config file against the schema definition",
    )

    return parser.parse_args()
