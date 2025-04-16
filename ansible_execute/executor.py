"""Playbook execution logic."""

import subprocess


def run_ansible_playbook(env: str) -> None:
    """
    Run the smoke test playbook, passing the environment as the 'nodes' variable.

    Args:
        env (str): Environment (dev, staging, prod), passed as --extra-vars nodes.
    """
    print(f"Running smoke test for environment: {env}")

    cmd = [
        "ansible-playbook",
        "ansible/playbooks/smoke_test.yml",
        "--extra-vars",
        f"nodes=[{env}]",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Playbook execution failed with exit code {exc.returncode}")
        raise SystemExit(exc.returncode) from exc
