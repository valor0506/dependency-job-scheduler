"""Unit tests for dependency validation and cycle detection."""

import unittest

from scheduler.graph import detect_cycles, validate_dependencies
from scheduler.models import ErrorCode, SchedulerError, Task
from scheduler.parser import open_csv_file, parse_tasks


class TestDependencyGraph(unittest.TestCase):
    """Test suite for dependency graph validation and cycle detection."""

    def test_valid_dag_passes(self):
        """A valid DAG should validate and pass cycle detection without error."""
        tasks = [
            Task(task_id="A", duration=3, priority=1, dependencies=()),
            Task(task_id="B", duration=2, priority=1, dependencies=("A",)),
            Task(task_id="C", duration=1, priority=1, dependencies=("B",)),
        ]
        validate_dependencies(tasks)
        detect_cycles(tasks)

    def test_unknown_dependency_raises_error(self):
        """Unknown dependency must raise INVALID_DEPENDENCY."""
        tasks = parse_tasks(open_csv_file("inputs/unknown-dependency.csv"))
        with self.assertRaises(SchedulerError) as ctx:
            validate_dependencies(tasks)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_DEPENDENCY)
        self.assertIn("depends on unknown task MISSING", ctx.exception.message)

    def test_self_dependency_raises_error(self):
        """Self-dependency must raise INVALID_DEPENDENCY."""
        tasks = [
            Task(task_id="A", duration=1, priority=0, dependencies=("A",))
        ]
        with self.assertRaises(SchedulerError) as ctx:
            validate_dependencies(tasks)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_DEPENDENCY)
        self.assertIn("cannot depend on itself", ctx.exception.message)

    def test_duplicate_dependency_raises_error(self):
        """Duplicate dependency tokens for the same task must raise INVALID_DEPENDENCY."""
        tasks = [
            Task(task_id="A", duration=1, priority=0, dependencies=()),
            Task(task_id="B", duration=1, priority=0, dependencies=("A", "A")),
        ]
        with self.assertRaises(SchedulerError) as ctx:
            validate_dependencies(tasks)
        self.assertEqual(ctx.exception.code, ErrorCode.INVALID_DEPENDENCY)
        self.assertIn("duplicate dependency", ctx.exception.message)

    def test_cycle_detection_on_cycle_csv(self):
        """inputs/cycle.csv must raise CYCLE_DETECTED with full path witness."""
        tasks = parse_tasks(open_csv_file("inputs/cycle.csv"))
        validate_dependencies(tasks)
        with self.assertRaises(SchedulerError) as ctx:
            detect_cycles(tasks)

        self.assertEqual(ctx.exception.code, ErrorCode.CYCLE_DETECTED)
        self.assertEqual(ctx.exception.cycle, ["A", "B", "C", "A"])
        self.assertIn("A -> B -> C -> A", ctx.exception.message)

    def test_two_node_cycle(self):
        """Two tasks mutually depending on each other must be detected."""
        tasks = [
            Task(task_id="X", duration=1, priority=1, dependencies=("Y",)),
            Task(task_id="Y", duration=1, priority=1, dependencies=("X",)),
        ]
        validate_dependencies(tasks)
        with self.assertRaises(SchedulerError) as ctx:
            detect_cycles(tasks)
        self.assertEqual(ctx.exception.code, ErrorCode.CYCLE_DETECTED)
        self.assertEqual(ctx.exception.cycle, ["X", "Y", "X"])


if __name__ == "__main__":
    unittest.main()

