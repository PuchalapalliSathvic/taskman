from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.task import Task, Priority, Status


class TaskRepository(ABC):

    @abstractmethod
    def save(self, task: Task) -> Task:
        ...

    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[Task]:
        ...

    @abstractmethod
    def find_all(self) -> List[Task]:
        ...

    @abstractmethod
    def find_by_status(self, status: Status) -> List[Task]:
        ...

    @abstractmethod
    def find_by_priority(self, priority: Priority) -> List[Task]:
        ...

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        ...
