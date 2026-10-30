# Assignment 1 — submission checklist

Complete this file in your public implementation repository. Submit its URL with your separate public Assignment 2 repository URL through the form supplied in the recruiter email; no commit SHA is required. Do not include personal information, customer data or credentials in either repository.

## Running the work

- Language/runtime and version: Python 3.10+ (tested on Python 3.15.0)
- Dependency installation command, if needed: None (built entirely using Python standard library)
- Exact scheduler command with `--input` and `--workers`:
  ```bash
  python3 -m scheduler.cli --input <PATH> --workers <W>
  ```
  Example:
  ```bash
  python3 -m scheduler.cli --input inputs/basic.csv --workers 2
  ```
- Exact test command:
  ```bash
  python3 -m unittest discover -s tests -p "test_*.py" -v
  ```
- Actual test results:
  ```text
  test_ascii_sorting_rules (test_engine.TestSchedulingEngine.test_ascii_sorting_rules) ... ok
  test_event_jumping_large_duration (test_engine.TestSchedulingEngine.test_event_jumping_large_duration) ... ok
  test_invalid_worker_bounds (test_engine.TestSchedulingEngine.test_invalid_worker_bounds) ... ok
  test_lowest_idle_worker_allocation (test_engine.TestSchedulingEngine.test_lowest_idle_worker_allocation) ... ok
  test_priority_and_ascii_tie_breaking (test_engine.TestSchedulingEngine.test_priority_and_ascii_tie_breaking) ... ok
  test_cycle_detection_on_cycle_csv (test_graph.TestDependencyGraph.test_cycle_detection_on_cycle_csv) ... ok
  test_duplicate_dependency_raises_error (test_graph.TestDependencyGraph.test_duplicate_dependency_raises_error) ... ok
  test_self_dependency_raises_error (test_graph.TestDependencyGraph.test_self_dependency_raises_error) ... ok
  test_two_node_cycle (test_graph.TestDependencyGraph.test_two_node_cycle) ... ok
  test_unknown_dependency_raises_error (test_graph.TestDependencyGraph.test_unknown_dependency_raises_error) ... ok
  test_valid_dag_passes (test_graph.TestDependencyGraph.test_valid_dag_passes) ... ok
  test_duplicate_task_id (test_parser.TestCSVParser.test_duplicate_task_id) ... ok
  test_duration_out_of_bounds (test_parser.TestCSVParser.test_duration_out_of_bounds) ... ok
  test_empty_dependency_token_rejected (test_parser.TestCSVParser.test_empty_dependency_token_rejected) ... ok
  test_invalid_header_raises_invalid_csv (test_parser.TestCSVParser.test_invalid_header_raises_invalid_csv) ... ok
  test_invalid_task_id_regex (test_parser.TestCSVParser.test_invalid_task_id_regex) ... ok
  test_missing_file_raises_read_error (test_parser.TestCSVParser.test_missing_file_raises_read_error) ... ok
  test_missing_header_raises_invalid_csv (test_parser.TestCSVParser.test_missing_header_raises_invalid_csv) ... ok
  test_parse_basic_file (test_parser.TestCSVParser.test_parse_basic_file) ... ok
  test_parse_empty_file (test_parser.TestCSVParser.test_parse_empty_file) ... ok
  test_signed_or_decimal_numbers_rejected (test_parser.TestCSVParser.test_signed_or_decimal_numbers_rejected) ... ok
  test_wrong_column_count_raises_invalid_csv (test_parser.TestCSVParser.test_wrong_column_count_raises_invalid_csv) ... ok
  test_basic_schedule (test_public.TestPublicCases.test_basic_schedule) ... ok
  test_cycle_detected_error (test_public.TestPublicCases.test_cycle_detected_error) ... ok
  test_duplicate_task_id_error (test_public.TestPublicCases.test_duplicate_task_id_error) ... ok
  test_empty_tasks (test_public.TestPublicCases.test_empty_tasks) ... ok
  test_idle_and_ties (test_public.TestPublicCases.test_idle_and_ties) ... ok
  test_simultaneous_completions (test_public.TestPublicCases.test_simultaneous_completions) ... ok
  test_unknown_dependency_error (test_public.TestPublicCases.test_unknown_dependency_error) ... ok

  Ran 29 tests in 0.003s
  OK
  ```
- Data structures and approximate time/space complexity:
  - **Data structures**:
    - `Task` / `ScheduleEntry` immutable dataclasses for domain entities.
    - `in_degree: dict[str, int]` for constant-time prerequisite tracking.
    - `dependents: dict[str, list[str]]` reverse adjacency list for fast dependent unblocking.
    - `ready_tasks: list[Task]` sorted deterministically by `(priority, task_id)`.
    - `idle_workers: set[int]` for tracking available worker IDs (`1..W`).
    - `running: list[tuple[int, int, Task]]` for tracking active tasks and jumping directly to the earliest completion timestamp.
  - **Time Complexity**:
    - Parsing and schema validation: $O(N)$ where $N$ is the number of rows ($\le 2000$).
    - Dependency integrity & Cycle detection (DFS): $O(V + E)$ where $V \le 2000$ and $E$ is the number of dependency relationships.
    - Discrete-event simulation: At most $V$ task completions. Each completion triggers dependent resolution and sorting of ready tasks: $O(V \log V + E)$.
    - Total Time Complexity: $O(V \log V + E)$, well under 10 milliseconds for the maximum 2,000 tasks.
  - **Space Complexity**:
    - $O(V + E)$ to store task entities, dependency graphs, and schedule history.

## Scope and assistance

- Known limitations or unfinished work: None within contract specifications. The scheduler strictly adheres to all validation boundaries, error formats, and deterministic tie-breaking rules.
- Documentation or libraries used: Python 3 standard library documentation (`csv`, `json`, `argparse`, `dataclasses`, `sys`, `unittest`).
- AI assistance used (or “none”), what it helped with and how you verified it:
  - Used AI pair programming to structure module boundaries, formulate test cases, and refine the DFS cycle path reconstruction algorithm.
  - Verified through manual code review and automated execution of 29 unit and regression tests, including cross-checking exact JSON outputs against all 7 candidate test cases.

## Before submitting

- [x] The repository includes implementation, executable tests and reproducible instructions.
- [x] Standard output is one JSON document; errors exit nonzero without a partial schedule.
- [x] The program runs locally without AI/LLM services, API keys or paid accounts.
- [x] No credentials, customer data, dependency folders or build output are included.
- [x] The repository is public and final work is on the default branch.
- [x] I will leave submitted work unchanged; no corrections or resubmissions are accepted.

You have two days from receiving the assignment; the recruiter email supplies the exact deadline (date, time and timezone), form URL and HR contact. Submit both repository links once. Extensions are considered only for a valid reason raised with HR; approval is not guaranteed and the deadline does not automatically pause. Contact HR for tooling or accessibility adjustments. Only candidates advancing receive a reply; next steps are communicated by email.
