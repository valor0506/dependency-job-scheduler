"""Dependency graph integrity validation and cycle detection."""

from scheduler.models import ErrorCode, SchedulerError, Task


def validate_dependencies(tasks: list[Task]) -> dict[str, Task]:
    """Validate dependency references for individual integrity.

    Checks:
        1. Duplicate dependencies within a single task (e.g. "B,B").
        2. Self-dependencies (e.g. task A depends on A).
        3. Unknown dependencies (dependency not present in the task list).

    Returns:
        Mapping of task_id to Task.

    Raises:
        SchedulerError: with INVALID_DEPENDENCY if any check fails.
    """
    task_map: dict[str, Task] = {t.task_id: t for t in tasks}

    for task in tasks:
        seen_deps: set[str] = set()
        for dep in task.dependencies:
            # Check for duplicate dependency
            if dep in seen_deps:
                raise SchedulerError(
                    ErrorCode.INVALID_DEPENDENCY,
                    f"Task '{task.task_id}' has duplicate dependency on '{dep}'.",
                )
            seen_deps.add(dep)

            # Check for self-dependency
            if dep == task.task_id:
                raise SchedulerError(
                    ErrorCode.INVALID_DEPENDENCY,
                    f"Task '{task.task_id}' cannot depend on itself.",
                )

            # Check for unknown dependency
            if dep not in task_map:
                raise SchedulerError(
                    ErrorCode.INVALID_DEPENDENCY,
                    f"Task {task.task_id} depends on unknown task {dep}",
                )

    return task_map


def detect_cycles(tasks: list[Task]) -> None:
    """Detect circular dependencies using Depth-First Search (DFS) with 3-color state.

    State definition:
        0 (UNVISITED): Node has not been visited yet.
        1 (VISITING): Node is in the current recursion stack (active path).
        2 (VISITED): Node and all its reachable dependencies have been verified acyclic.

    Raises:
        SchedulerError: with CYCLE_DETECTED and the reconstructed closed cycle path
                        if a dependency loop exists.
    """
    task_map = {t.task_id: t for t in tasks}

    # States: 0 = unvisited, 1 = visiting, 2 = visited
    state: dict[str, int] = {t.task_id: 0 for t in tasks}

    # Track recursion path to reconstruct cycle
    path: list[str] = []

    def dfs(node_id: str) -> None:
        state[node_id] = 1
        path.append(node_id)

        task = task_map[node_id]
        for dep_id in task.dependencies:
            dep_state = state.get(dep_id, 0)
            if dep_state == 1:
                # Cycle detected! Reconstruct the closed loop
                cycle_start_idx = path.index(dep_id)
                cycle_path = path[cycle_start_idx:] + [dep_id]
                cycle_str = " -> ".join(cycle_path)
                raise SchedulerError(
                    ErrorCode.CYCLE_DETECTED,
                    f"Dependency cycle {cycle_str}",
                    cycle=cycle_path,
                )
            elif dep_state == 0:
                dfs(dep_id)

        path.pop()
        state[node_id] = 2

    # Iterate deterministically through all tasks
    for task in tasks:
        if state[task.task_id] == 0:
            dfs(task.task_id)

