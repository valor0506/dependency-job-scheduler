"""Deterministic discrete-event scheduling engine."""

from scheduler.models import (
    ErrorCode,
    ScheduleEntry,
    ScheduleResult,
    SchedulerError,
    Task,
)

MIN_WORKERS = 1
MAX_WORKERS = 32


def validate_worker_count(workers: int) -> None:
    """Validate that worker count is within specification bounds [1, 32]."""
    if not isinstance(workers, int) or not (MIN_WORKERS <= workers <= MAX_WORKERS):
        raise SchedulerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Worker count {workers} out of bounds: must be an integer between {MIN_WORKERS} and {MAX_WORKERS}.",
        )


def schedule_tasks(tasks: list[Task], workers: int) -> ScheduleResult:
    """Simulate task execution using deterministic discrete-event scheduling.

    Rules implemented:
        1. A task starts only after all of its dependencies have finished.
        2. Simultaneous task completions are processed together before selecting new work.
        3. Ready tasks are prioritized by (priority ASC, task_id ASCII ASC).
        4. Tasks are assigned to the lowest-numbered idle worker.
        5. Virtual time jumps directly to the next completion event (no wall-clock delay).
        6. Completed schedule is sorted by start ASC, then worker_id ASC.
    """
    validate_worker_count(workers)

    # Fast path for empty task set
    if not tasks:
        return ScheduleResult(workers=workers, makespan=0, schedule=[])

    # 1. Build in-degree counts and reverse dependency graph (dependents)
    task_map: dict[str, Task] = {t.task_id: t for t in tasks}
    in_degree: dict[str, int] = {t.task_id: len(t.dependencies) for t in tasks}
    dependents: dict[str, list[str]] = {t.task_id: [] for t in tasks}

    for t in tasks:
        for dep in t.dependencies:
            dependents[dep].append(t.task_id)

    # 2. Initialize simulation state
    current_time: int = 0
    # Available idle workers (integers 1..workers)
    idle_workers: set[int] = set(range(1, workers + 1))
    # Tasks ready to execute
    ready_tasks: list[Task] = [t for t in tasks if in_degree[t.task_id] == 0]
    # Running tasks: list of (end_time, worker_id, Task)
    running: list[tuple[int, int, Task]] = []
    # Recorded schedule entries
    completed_entries: list[ScheduleEntry] = []

    # 3. Main Discrete-Event Simulation Loop
    while ready_tasks or running:
        # Phase A: Assign ready tasks to idle workers at current_time
        if ready_tasks and idle_workers:
            # Sort ready tasks deterministically: priority ASC, then ASCII task_id ASC
            ready_tasks.sort(key=lambda t: (t.priority, t.task_id))
            # Sort idle workers ascending: lowest-numbered worker first
            available_workers = sorted(idle_workers)

            assigned_count = min(len(ready_tasks), len(available_workers))
            tasks_to_assign = ready_tasks[:assigned_count]
            workers_to_use = available_workers[:assigned_count]

            # Remove assigned tasks from ready queue and workers from idle set
            ready_tasks = ready_tasks[assigned_count:]
            for w in workers_to_use:
                idle_workers.remove(w)

            # Start execution for each assigned pair
            for task, w_id in zip(tasks_to_assign, workers_to_use):
                end_time = current_time + task.duration
                running.append((end_time, w_id, task))
                completed_entries.append(
                    ScheduleEntry(
                        task_id=task.task_id,
                        worker_id=w_id,
                        start=current_time,
                        end=end_time,
                    )
                )

        # If nothing is running and no tasks are ready, we are done
        if not running:
            break

        # Phase B: Advance virtual time directly to the earliest completion event
        # If there are still ready tasks but no idle workers, or no ready tasks:
        # Jump directly to the next completion time!
        next_event_time = min(item[0] for item in running)
        current_time = next_event_time

        # Phase C: Complete ALL tasks finishing at next_event_time simultaneously
        still_running: list[tuple[int, int, Task]] = []
        finished_tasks: list[Task] = []

        for end_t, w_id, task in running:
            if end_t == current_time:
                idle_workers.add(w_id)
                finished_tasks.append(task)
            else:
                still_running.append((end_t, w_id, task))

        running = still_running

        # Phase D: Release newly unblocked tasks whose dependencies are now satisfied
        newly_ready: list[Task] = []
        for finished in finished_tasks:
            for dep_id in dependents[finished.task_id]:
                in_degree[dep_id] -= 1
                if in_degree[dep_id] == 0:
                    newly_ready.append(task_map[dep_id])

        # Add newly ready tasks to the ready pool
        ready_tasks.extend(newly_ready)

    # 4. Format and sort final output entries
    # Spec requirement: "Output entries sorted by start ascending, then worker_id ascending."
    completed_entries.sort(key=lambda e: (e.start, e.worker_id))

    makespan = max((e.end for e in completed_entries), default=0)

    return ScheduleResult(
        workers=workers,
        makespan=makespan,
        schedule=completed_entries,
    )

