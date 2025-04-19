"""Playbook execution logic."""

import logging
import subprocess
import json

logger = logging.getLogger(__name__)


def run_ansible_playbook(env: str) -> None:
    """
    Run the ansible playbook, passing the environment as the 'nodes' variable.

    Args:
        env (str): Environment (dev, staging, prod), passed as --extra-vars nodes.
    """
    logger.info("Starting execution for environment: %s", env)
    # Build extra‑vars as a proper JSON object:
    vars_json = json.dumps({"nodes": [env]})
    cmd = [
        "ansible-playbook",
        "ansible/playbooks/smoke_test.yml",
        "--extra-vars",
        vars_json,
    ]
    logger.debug("Running command: %r", cmd)

    try:
        subprocess.run(cmd, check=True)
        logger.info("Playbook executed successfully")
    except subprocess.CalledProcessError as exc:
        logger.error(
            "Playbook execution failed with exit code %d", exc.returncode, exc_info=True
        )
        # Mirror the old behavior of exiting with the same code.
        raise SystemExit(exc.returncode) from exc
