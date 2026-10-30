# Dependency-Aware Job Scheduler

A deterministic, discrete-event command-line job scheduler built with Python 3 (standard library). The scheduler parses task definitions and dependency constraints from a CSV input, validates graph integrity, and simulates multi-worker task execution using priority and ASCII tie-breaking policies.

---

## 1. Project Overview

In multi-task processing systems, tasks often depend on the completion of prior tasks and compete for a fixed pool of workers. This project implements an offline discrete-event scheduling simulator that:
- Reads tasks, durations, priorities, and dependency relationships from a CSV file.
- Strictly validates input schemas and detects dependency anomalies (missing references, self-dependencies, duplicate IDs, and circular dependency cycles).
- Simulates worker allocations in **virtual time** using an event-jumping mechanism (no wall-clock delays).
- Generates a deterministic execution schedule formatted as JSON.

---

## 2. Key Features

- **Strict Validation**: Validates task identifiers against ASCII specifications, checks bounds for duration and priority, and rejects malformed records.
- **Cycle Detection with Path Witness**: Identifies circular dependencies using Depth-First Search (DFS) and reports the exact closed dependency chain.
- **Deterministic Scheduling Engine**:
  - Unblocks tasks only when all dependencies are satisfied.
  - Prioritizes tasks with smaller priority values, resolving ties using ASCII lexicographical order of task IDs.
  - Allocates ready tasks to the lowest-numbered available workers.
  - Handles simultaneous completions by releasing all newly eligible tasks before assigning the next unit of work.
- **Zero External Dependencies**: Implemented purely using the Python 3 standard library (`csv`, `json`, `argparse`, `dataclasses`, `sys`, `unittest`).

---

## 3. Project Architecture

```text
.
├── scheduler/
│   ├── __init__.py
│   ├── cli.py             # CLI argument parsing and process entry point
│   ├── models.py          # Data classes (Task, ScheduleEntry, ErrorResponse)
│   ├── parser.py          # Robust CSV reader, whitespace trimmer, and schema validator
│   ├── graph.py           # Dependency resolution and DFS cycle detection
│   └── engine.py          # Discrete-event simulation scheduler
├── tests/
│   ├── __init__.py
│   ├── test_public.py     # End-to-end verification against candidate test cases
│   ├── test_validation.py # Unit tests for malformed inputs, boundaries, duplicates
│   └── test_engine.py     # Unit tests for scheduling edge cases (ties, idle periods)
├── inputs/                # Public test CSV files
├── expected/              # Ground truth JSON outputs
├── SUBMISSION.md          # Formal candidate submission checklist
├── README.md              # Project documentation
└── .gitignore
```

---

## 4. Quick Start

### Prerequisites
- Python 3.10+ (Standard library only; no external package installation required)

### Running the Scheduler
```bash
python3 -m scheduler.cli --input inputs/basic.csv --workers 2
```

### Running the Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 5. Specification Compliance

- **CLI flags**: `--input PATH --workers W` (where `1 <= W <= 32`).
- **Exit codes**: Returns `0` on successful schedule generation, non-zero (`1`) on any input or validation error.
- **Output format**: Standard output emits strictly one valid JSON document. Diagnostic logs (if any) are redirected to standard error.
