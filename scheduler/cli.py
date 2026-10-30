"""Command-line interface (CLI) entry point for the job scheduler."""

import argparse
import json
import sys

from scheduler.engine import schedule_tasks
from scheduler.graph import detect_cycles, validate_dependencies
from scheduler.models import ErrorCode, SchedulerError
from scheduler.parser import open_csv_file, parse_tasks


class SpecArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that formats errors to the specification JSON schema."""

    def error(self, message: str) -> None:
        err = SchedulerError(
            code=ErrorCode.INVALID_ARGUMENT,
            message=f"Command-line argument error: {message}",
        )
        sys.stdout.write(json.dumps(err.to_dict(), indent=2) + "\n")
        sys.exit(1)


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI flags --input PATH and --workers W."""
    parser = SpecArgumentParser(
        prog="scheduler",
        description="Dependency-aware job scheduler simulator.",
        add_help=True,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the tasks CSV file.",
    )
    parser.add_argument(
        "--workers",
        required=True,
        type=int,
        help="Number of workers (integer between 1 and 32).",
    )
    return parser.parse_args(argv)


def run_pipeline(input_path: str, workers: int) -> int:
    """Execute the complete scheduler pipeline.

    Returns:
        0 on success, 1 on any error.
    """
    try:
        # 1. Read input file
        stream = open_csv_file(input_path)

        # 2. Parse CSV rows and validate schema bounds
        tasks = parse_tasks(stream)

        # 3. Validate dependency integrity
        validate_dependencies(tasks)

        # 4. Check for dependency cycles
        detect_cycles(tasks)

        # 5. Run simulation engine
        result = schedule_tasks(tasks, workers)

        # 6. Emit schedule JSON to stdout
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
        return 0

    except SchedulerError as exc:
        sys.stdout.write(json.dumps(exc.to_dict(), indent=2) + "\n")
        return 1
    except Exception as exc:  # Catch unexpected runtime exceptions
        err = SchedulerError(ErrorCode.READ_ERROR, f"Unexpected error: {exc}")
        sys.stdout.write(json.dumps(err.to_dict(), indent=2) + "\n")
        return 1


def main() -> None:
    """Main CLI entrypoint."""
    args = parse_cli_args()
    exit_code = run_pipeline(input_path=args.input, workers=args.workers)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

