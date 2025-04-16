"""Command-line interface for Ansible execution tool."""

import argparse
from argparse import Namespace


def parse_args() -> Namespace:
    """
    Parse command-line arguments.

    Returns:
        Namespace: Parsed arguments with `env` attribute.
    """
    parser = argparse.ArgumentParser(
        description="Ansible execution CLI for homelab environments"
    )
    parser.add_argument(
        "-e",
        "--env",
        required=True,
        choices=["dev", "staging", "prod"],
        help="Target environment (dev, staging, prod)",
    )
    return parser.parse_args()
