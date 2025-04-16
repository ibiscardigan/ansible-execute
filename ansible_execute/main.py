"""Entry point for Ansible execution tool."""

from ansible_execute import cli
from ansible_execute import executor


def main() -> None:
    """Main entry point for the CLI tool."""
    args = cli.parse_args()
    print(f"Environment selected: {args.env}")

    executor.run_ansible_playbook(env=args.env)


if __name__ == "__main__":
    main()
