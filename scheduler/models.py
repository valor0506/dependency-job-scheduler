"""Data models, domain entities, and error definitions for the scheduler."""

from dataclasses import dataclass, field


# ==========================================
# 1. Core Domain Models (Success Path)
# ==========================================

@dataclass(frozen=True)
class Task:
    """Represents a validated task entity from the input CSV."""

    task_id: str
    duration: int
    priority: int
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScheduleEntry:
    """Represents the scheduling allocation for a single completed task."""

    task_id: str
    worker_id: int
    start: int
    end: int

    def to_dict(self) -> dict:
        """Convert entry to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "start": self.start,
            "end": self.end,
        }


@dataclass
class ScheduleResult:
    """Represents the final successful schedule output."""

    workers: int
    makespan: int
    schedule: list[ScheduleEntry] = field(default_factory=list)
    status: str = "ok"

    def to_dict(self) -> dict:
        """Convert schedule result to the output schema specified in SPECIFICATION.md."""
        return {
            "status": self.status,
            "workers": self.workers,
            "makespan": self.makespan,
            "schedule": [entry.to_dict() for entry in self.schedule],
        }
