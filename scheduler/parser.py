"""CSV input parser and schema validator."""

import csv
import io
import os
import re
from typing import TextIO

from scheduler.models import ErrorCode, SchedulerError, Task

# Required CSV header specification (case-sensitive, exact order)
REQUIRED_HEADER = ["task_id", "duration", "priority", "dependencies"]

# task_id: ASCII matching [A-Za-z][A-Za-z0-9_-]{0,31}
TASK_ID_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")

# Maximum allowed tasks in a single file
MAX_TASKS = 2000

# Bounds for duration and priority
MIN_DURATION = 1
MAX_DURATION = 1_000_000
MIN_PRIORITY = 0
MAX_PRIORITY = 1000



def open_csv_file(path: str) -> io.StringIO:
    """Open and read a CSV file with UTF-8 (and optional UTF-8 BOM) encoding.

    Raises:
        SchedulerError: with READ_ERROR if file is missing or unreadable,
                        or INVALID_CSV if file cannot be decoded as UTF-8.
    """
    if not os.path.exists(path):
        raise SchedulerError(ErrorCode.READ_ERROR, f"Input file not found: {path}")

    try:
        # 'utf-8-sig' automatically strips any UTF-8 BOM if present
        with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
            content = f.read()
    except UnicodeDecodeError as exc:
        raise SchedulerError(ErrorCode.INVALID_CSV, f"File encoding is not valid UTF-8: {exc}") from exc
    except OSError as exc:
        raise SchedulerError(ErrorCode.READ_ERROR, f"Cannot read input file: {exc}") from exc

    return io.StringIO(content)


def _validate_decimal_digits(val: str, field_name: str) -> int:
    """Ensure string consists strictly of ASCII digits (no signs, decimals) and parse to int."""
    if not val or not val.isdigit():
        raise SchedulerError(
            ErrorCode.INVALID_TASK,
            f"Invalid {field_name} value '{val}': must be an unsigned integer without signs or decimals.",
        )
    return int(val)


def parse_tasks(stream: TextIO) -> list[Task]:
    """Parse and validate task definitions from a CSV stream.

    Raises:
        SchedulerError: with INVALID_CSV, INVALID_TASK, DUPLICATE_TASK, or
                        INVALID_DEPENDENCY on validation failure.
    """
    reader = csv.reader(stream)

    # 1. Read and validate header
    try:
        raw_header = next(reader)
    except StopIteration:
        raise SchedulerError(ErrorCode.INVALID_CSV, "CSV file is empty; missing required header.")

    header = [col.strip() for col in raw_header]
    if header != REQUIRED_HEADER:
        raise SchedulerError(
            ErrorCode.INVALID_CSV,
            f"Invalid header {header}; expected exactly {REQUIRED_HEADER}",
        )

    tasks: list[Task] = []
    seen_ids: set[str] = set()

    # 2. Iterate through rows
    for row_idx, raw_row in enumerate(reader, start=2):
        # Ignore truly empty lines (e.g. from blank lines in CSV)
        if not raw_row or (len(raw_row) == 1 and not raw_row[0].strip()):
            continue

        # Column count check
        if len(raw_row) != 4:
            raise SchedulerError(
                ErrorCode.INVALID_CSV,
                f"Row {row_idx} has {len(raw_row)} columns; expected exactly 4.",
            )

        task_id = raw_row[0].strip()
        duration_raw = raw_row[1].strip()
        priority_raw = raw_row[2].strip()
        dependencies_raw = raw_row[3].strip()

        # Validate task_id syntax
        if not TASK_ID_REGEX.match(task_id):
            raise SchedulerError(
                ErrorCode.INVALID_TASK,
                f"Invalid task_id '{task_id}' at row {row_idx}: must match pattern [A-Za-z][A-Za-z0-9_-]{{0,31}}",
            )

        # Check uniqueness of task_id
        if task_id in seen_ids:
            raise SchedulerError(
                ErrorCode.DUPLICATE_TASK,
                f"Task ID {task_id} occurs more than once",
            )
        seen_ids.add(task_id)

        # Validate duration
        duration = _validate_decimal_digits(duration_raw, "duration")
        if not (MIN_DURATION <= duration <= MAX_DURATION):
            raise SchedulerError(
                ErrorCode.INVALID_TASK,
                f"Duration {duration} out of bounds [{MIN_DURATION}, {MAX_DURATION}] at row {row_idx}.",
            )

        # Validate priority
        priority = _validate_decimal_digits(priority_raw, "priority")
        if not (MIN_PRIORITY <= priority <= MAX_PRIORITY):
            raise SchedulerError(
                ErrorCode.INVALID_TASK,
                f"Priority {priority} out of bounds [{MIN_PRIORITY}, {MAX_PRIORITY}] at row {row_idx}.",
            )

        # Extract dependencies tokens
        if not dependencies_raw:
            deps: tuple[str, ...] = ()
        else:
            raw_tokens = dependencies_raw.split(",")
            dep_list = []
            for token in raw_tokens:
                trimmed = token.strip()
                if not trimmed:
                    raise SchedulerError(
                        ErrorCode.INVALID_DEPENDENCY,
                        f"Task '{task_id}' contains an empty dependency token in '{dependencies_raw}'.",
                    )
                dep_list.append(trimmed)
            deps = tuple(dep_list)

        tasks.append(Task(task_id=task_id, duration=duration, priority=priority, dependencies=deps))

        # Check maximum task limit
        if len(tasks) > MAX_TASKS:
            raise SchedulerError(
                ErrorCode.INVALID_TASK,
                f"Task count exceeds maximum allowed limit of {MAX_TASKS}.",
            )

    return tasks

