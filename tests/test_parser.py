"""Unit tests for CSV parser and schema validation."""

import io
import unittest

from scheduler.models import ErrorCode, SchedulerError
from scheduler.parser import open_csv_file, parse_tasks


class TestCSVParser(unittest.TestCase):
    """Test suite for CSV parser edge cases and validations."""

    def test_parse_basic_file(self):
        """Test parsing valid basic.csv."""
        tasks = parse_tasks(open_csv_file("inputs/basic.csv"))
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0].task_id, "A")
        self.assertEqual(tasks[0].duration, 3)
        self.assertEqual(tasks[0].priority, 2)
        self.assertEqual(tasks[0].dependencies, ())
        self.assertEqual(tasks[3].task_id, "D")
        self.assertEqual(tasks[3].dependencies, ("B", "C"))

    def test_parse_empty_file(self):
        """A header-only file represents zero tasks and is valid."""
        tasks = parse_tasks(open_csv_file("inputs/empty.csv"))
        self.assertEqual(len(tasks), 0)

    def test_missing_file_raises_read_error(self):
        """Missing file must raise READ_ERROR."""
        with self.assertRaises(SchedulerError) as ctx:
            open_csv_file("inputs/non_existent_file.csv")
        self.assertEqual(ctx.exception.code, ErrorCode.READ_ERROR)

    def test_missing_header_raises_invalid_csv(self):
        """An empty file without a header must raise INVALID_CSV."""
        stream = io.StringIO("")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_CSV)

    def test_invalid_header_raises_invalid_csv(self):
        """Incorrect column names must raise INVALID_CSV."""
        stream = io.StringIO("id,dur,prio,deps\nA,1,1,")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_CSV)

    def test_wrong_column_count_raises_invalid_csv(self):
        """Row with incorrect column count must raise INVALID_CSV."""
        stream = io.StringIO("task_id,duration,priority,dependencies\nA,1,1")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_CSV)

    def test_invalid_task_id_regex(self):
        """Task ID starting with a digit or symbol must raise INVALID_TASK."""
        stream = io.StringIO("task_id,duration,priority,dependencies\n1Invalid,1,1,")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_TASK)

    def test_duplicate_task_id(self):
        """Duplicate task ID must raise DUPLICATE_TASK."""
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(open_csv_file("inputs/duplicate-id.csv"))
        self.assertEqual(ctx.exception.code, ErrorCode.DUPLICATE_TASK)

    def test_duration_out_of_bounds(self):
        """Duration 0 or > 1_000_000 must raise INVALID_TASK."""
        stream_zero = io.StringIO("task_id,duration,priority,dependencies\nA,0,1,")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream_zero)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_TASK)

    def test_signed_or_decimal_numbers_rejected(self):
        """Negative numbers or decimals must raise INVALID_TASK."""
        stream_neg = io.StringIO("task_id,duration,priority,dependencies\nA,-5,1,")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream_neg)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_TASK)

        stream_float = io.StringIO("task_id,duration,priority,dependencies\nA,5,1.5,")
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream_float)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_TASK)

    def test_empty_dependency_token_rejected(self):
        """Empty dependency token like 'A,,B' must raise INVALID_DEPENDENCY."""
        stream = io.StringIO('task_id,duration,priority,dependencies\nA,1,1,\nB,1,1,"A,,C"')
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(stream)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_DEPENDENCY)


if __name__ == "__main__":
    unittest.main()
