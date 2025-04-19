"""Playbook execution logic."""

import logging
import subprocess
import json

logger = logging.getLogger(__name__)


def run_ansible_playbook(env: str, playbook: str, verbosity: int = 0) -> None:
    """
    Run the ansible playbook, passing the environment as the 'nodes' variable.

    Args:
        env (str): Environment (dev, staging, prod), passed as --extra-vars nodes.
        verbosity (int): Verbosity level from CLI (-v, -vv, etc).
    """
    logger.info("Starting execution for environment: %s", env)

    vars_json = json.dumps({"nodes": [env]})
    cmd = [
        "ansible-playbook",
        f"ansible/playbooks/{playbook}.yml",
        "--extra-vars",
        vars_json,
    ]

    if verbosity > 0:
        cmd.append("-" + "v" * verbosity)

    logger.debug("Running command: %r", cmd)

    try:
        subprocess.run(cmd, check=True)
        logger.info("Playbook executed successfully")
    except subprocess.CalledProcessError as exc:
        logger.error(
            "Playbook execution failed with exit code %d", exc.returncode, exc_info=True
        )
        raise SystemExit(exc.returncode) from exc
