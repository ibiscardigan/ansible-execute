"""Custom exceptions for ansible-execute.

This module defines domain-specific exception types for use throughout
the ansible-execute CLI tool.
"""


class ConfigError(Exception):
    """Raised when configuration validation fails or is improperly structured."""
