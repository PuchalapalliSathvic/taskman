import json
import os
from datetime import datetime
from typing import List, Optional

from domain.entities.task import Task, Priority, Status
from domain.repositories.task_repository import TaskRepository


class JsonFileTaskRepository(TaskRepository):

    def __init__(self, filepath: str = "~/.taskman/tasks.json"):
        self._filepath = os.path.expanduser(filepath)
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if not os.path.exists(self._filepath):
            self._write({})

    def _read(self) -> dict:
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _serialize(self, task: Task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    def _deserialize(self, data: dict) -> Task:
        task = Task(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            id=data["id"],
        )
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        return task

    def save(self, task: Task) -> Task:
        data = self._read()
        data[task.id] = self._serialize(task)
        self._write(data)
        return task

    def find_by_id(self, task_id: str) -> Optional[Task]:
        data = self._read()
        for key, value in data.items():
            if key == task_id or key.startswith(task_id):
                return self._deserialize(value)
        return None

    def find_all(self) -> List[Task]:
        return [self._deserialize(v) for v in self._read().values()]

    def find_by_status(self, status: Status) -> List[Task]:
        return [t for t in self.find_all() if t.status == status]

    def find_by_priority(self, priority: Priority) -> List[Task]:
        return [t for t in self.find_all() if t.priority == priority]

    def delete(self, task_id: str) -> bool:
        data = self._read()
        for key in list(data.keys()):
            if key == task_id or key.startswith(task_id):
                del data[key]
                self._write(data)
                return True
        return False
