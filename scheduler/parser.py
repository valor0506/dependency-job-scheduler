"""CSV input parser and schema validator."""

import csv
import io
import os
import re
from typing import TextIO

from scheduler.models import ErrorCode, SchedulerError, Task

# Required CSV header specification (case-sensitive, exact order)
REQUIRED_HEADER = ["task_id", "duration", "priority", "dependencies"]


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
