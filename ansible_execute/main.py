"""Entry point for Ansible execution tool."""

import logging
import yaml

from ansible_execute import cli, executor, logger as log_setup, utils


def main() -> None:
    """Main entry point for the CLI tool."""
    args = cli.parse_args()

    # Always try to load config first
    config = None
    log_dir = None
    try:
        config = utils.Config(config_path=args.config)
        log_dir_value = config.config_data.get("logging", {}).get("dir")
        if log_dir_value:
            log_dir = utils.pathlib.Path(log_dir_value)
    except (utils.exceptions.ConfigError, FileNotFoundError, yaml.YAMLError, OSError):
        # Config may be missing/invalid for generate/validate paths
        pass

    # Configure structured logging based on CLI args and/or config
    log_setup.configure_logging(
        verbosity=args.verbose,
        log_directory=log_dir,
        non_interactive=getattr(args, "non_interactive", False),
    )
    logger = logging.getLogger(__name__)

    for key, value in vars(args).items():
        logger.debug(f"Arg {key}: {value}")

    # Handle --generate-config
    if args.generate_config:
        logger.info(f"Generating default config at: {args.generate_config}")
        utils.ConfigGenerator().generate(output_path=args.generate_config)
        return

    # Handle --validate-config
    if args.validate_config:
        logger.info(f"Validating config: {args.config}")
        utils.Config(config_path=args.config)
        logger.info("Configuration is valid.")
        return

    # Normal execution path
    if not args.test:
        logger.info("Running Ansible playbook...")
        executor.run_ansible_playbook(env=args.env)
    else:
        logger.info(f"Test mode enabled, skipping playbook execution for {args.env}.")


if __name__ == "__main__":
    main()
