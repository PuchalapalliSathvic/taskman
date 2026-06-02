from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateTaskRequest:
    title: str
    description: str = ""
    priority: str = "medium"


@dataclass
class UpdateTaskRequest:
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None


@dataclass
class TaskResponse:
    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    updated_at: str

    @classmethod
    def from_task(cls, task) -> "TaskResponse":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority.value,
            status=task.status.value,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )
