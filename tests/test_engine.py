"""Unit tests for discrete-event scheduling engine."""

import unittest

from scheduler.engine import schedule_tasks
from scheduler.models import ErrorCode, SchedulerError, Task


class TestSchedulingEngine(unittest.TestCase):
    """Test suite for scheduling engine mechanics, tie-breaking, and worker allocations."""

    def test_invalid_worker_bounds(self):
        """Workers < 1 or > 32 must raise INVALID_ARGUMENT."""
        tasks = [Task(task_id="A", duration=1, priority=1, dependencies=())]
        with self.assertRaises(SchedulerError) as ctx_0:
            schedule_tasks(tasks, workers=0)
        self.assertEqual(ctx_0.exception.code, ErrorCode.INVALID_ARGUMENT)

        with self.assertRaises(SchedulerError) as ctx_33:
            schedule_tasks(tasks, workers=33)
        self.assertEqual(ctx_33.exception.code, ErrorCode.INVALID_ARGUMENT)

    def test_priority_and_ascii_tie_breaking(self):
        """Ready tasks must sort by priority ascending, then task ID ASCII ascending."""
        # Tasks are provided in reverse priority and reverse alphabetical order
        tasks = [
            Task(task_id="D", duration=2, priority=2, dependencies=()),
            Task(task_id="B", duration=2, priority=1, dependencies=()),
            Task(task_id="A", duration=2, priority=1, dependencies=()),
            Task(task_id="C", duration=2, priority=0, dependencies=()),
        ]
        # With 1 worker, order must strictly be: C (prio 0), A (prio 1, id 'A'), B (prio 1, id 'B'), D (prio 2)
        res = schedule_tasks(tasks, workers=1)
        executed_order = [entry.task_id for entry in res.schedule]
        self.assertEqual(executed_order, ["C", "A", "B", "D"])

    def test_ascii_sorting_rules(self):
        """ASCII order means 'J10' < 'J2' and uppercase < lowercase."""
        tasks = [
            Task(task_id="J2", duration=1, priority=0, dependencies=()),
            Task(task_id="J10", duration=1, priority=0, dependencies=()),
            Task(task_id="b", duration=1, priority=0, dependencies=()),
            Task(task_id="A", duration=1, priority=0, dependencies=()),
        ]
        res = schedule_tasks(tasks, workers=1)
        executed_order = [entry.task_id for entry in res.schedule]
        self.assertEqual(executed_order, ["A", "J10", "J2", "b"])

    def test_lowest_idle_worker_allocation(self):
        """When multiple workers are idle, tasks are assigned to lowest worker IDs first."""
        tasks = [
            Task(task_id="T1", duration=5, priority=0, dependencies=()),
            Task(task_id="T2", duration=2, priority=0, dependencies=()),
        ]
        # 3 workers available: Worker 1 takes T1, Worker 2 takes T2, Worker 3 stays idle
        res = schedule_tasks(tasks, workers=3)
        self.assertEqual(res.schedule[0].worker_id, 1)
        self.assertEqual(res.schedule[1].worker_id, 2)

    def test_event_jumping_large_duration(self):
        """Engine must jump virtual time directly without looping or delay."""
        tasks = [
            Task(task_id="A", duration=500_000, priority=0, dependencies=()),
            Task(task_id="B", duration=500_000, priority=0, dependencies=("A",)),
        ]
        res = schedule_tasks(tasks, workers=1)
        self.assertEqual(res.makespan, 1_000_000)
        self.assertEqual(res.schedule[0].start, 0)
        self.assertEqual(res.schedule[0].end, 500_000)
        self.assertEqual(res.schedule[1].start, 500_000)
        self.assertEqual(res.schedule[1].end, 1_000_000)


if __name__ == "__main__":
    unittest.main()

