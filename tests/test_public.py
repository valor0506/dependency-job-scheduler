"""End-to-end tests verifying candidate inputs against expected outputs."""

import json
import unittest

from scheduler.cli import run_pipeline
from scheduler.engine import schedule_tasks
from scheduler.graph import detect_cycles, validate_dependencies
from scheduler.models import ErrorCode, SchedulerError
from scheduler.parser import open_csv_file, parse_tasks


class TestPublicCases(unittest.TestCase):
    """Verify all 7 candidate test cases from the recruitment packet."""

    def test_basic_schedule(self):
        """inputs/basic.csv with 2 workers -> expected/basic.json."""
        tasks = parse_tasks(open_csv_file("inputs/basic.csv"))
        validate_dependencies(tasks)
        detect_cycles(tasks)
        res = schedule_tasks(tasks, workers=2)

        with open("expected/basic.json") as f:
            expected = json.load(f)

        self.assertEqual(res.to_dict(), expected)

    def test_simultaneous_completions(self):
        """inputs/simultaneous.csv with 2 workers -> expected/simultaneous.json."""
        tasks = parse_tasks(open_csv_file("inputs/simultaneous.csv"))
        validate_dependencies(tasks)
        detect_cycles(tasks)
        res = schedule_tasks(tasks, workers=2)

        with open("expected/simultaneous.json") as f:
            expected = json.load(f)

        self.assertEqual(res.to_dict(), expected)

    def test_idle_and_ties(self):
        """inputs/idle-and-ties.csv with 3 workers -> expected/idle-and-ties.json."""
        tasks = parse_tasks(open_csv_file("inputs/idle-and-ties.csv"))
        validate_dependencies(tasks)
        detect_cycles(tasks)
        res = schedule_tasks(tasks, workers=3)

        with open("expected/idle-and-ties.json") as f:
            expected = json.load(f)

        self.assertEqual(res.to_dict(), expected)

    def test_empty_tasks(self):
        """inputs/empty.csv with 2 workers -> expected/empty.json."""
        tasks = parse_tasks(open_csv_file("inputs/empty.csv"))
        validate_dependencies(tasks)
        detect_cycles(tasks)
        res = schedule_tasks(tasks, workers=2)

        with open("expected/empty.json") as f:
            expected = json.load(f)

        self.assertEqual(res.to_dict(), expected)

    def test_unknown_dependency_error(self):
        """inputs/unknown-dependency.csv with 2 workers -> expected/unknown-dependency.json."""
        tasks = parse_tasks(open_csv_file("inputs/unknown-dependency.csv"))
        with self.assertRaises(SchedulerError) as ctx:
            validate_dependencies(tasks)

        with open("expected/unknown-dependency.json") as f:
            expected = json.load(f)

        self.assertEqual(ctx.exception.to_dict(), expected)

    def test_cycle_detected_error(self):
        """inputs/cycle.csv with 2 workers -> expected/cycle.json."""
        tasks = parse_tasks(open_csv_file("inputs/cycle.csv"))
        validate_dependencies(tasks)
        with self.assertRaises(SchedulerError) as ctx:
            detect_cycles(tasks)

        with open("expected/cycle.json") as f:
            expected = json.load(f)

        self.assertEqual(ctx.exception.to_dict(), expected)

    def test_duplicate_task_id_error(self):
        """inputs/duplicate-id.csv with 2 workers -> expected/duplicate-id.json."""
        with self.assertRaises(SchedulerError) as ctx:
            parse_tasks(open_csv_file("inputs/duplicate-id.csv"))

        with open("expected/duplicate-id.json") as f:
            expected = json.load(f)

        self.assertEqual(ctx.exception.to_dict(), expected)


if __name__ == "__main__":
    unittest.main()

