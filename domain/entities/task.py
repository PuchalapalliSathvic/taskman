from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class Task:
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def complete(self) -> None:
        if self.status == Status.DONE:
            raise ValueError(f"Task '{self.title}' is already completed.")
        self.status = Status.DONE
        self.updated_at = datetime.utcnow()

    def start(self) -> None:
        if self.status == Status.DONE:
            raise ValueError(f"Task '{self.title}' is already completed.")
        self.status = Status.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def update_title(self, title: str) -> None:
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        self.title = title.strip()
        self.updated_at = datetime.utcnow()

    def is_high_priority(self) -> bool:
        return self.priority == Priority.HIGH
