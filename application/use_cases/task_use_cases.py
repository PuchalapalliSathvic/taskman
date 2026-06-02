from typing import List

from application.dtos import CreateTaskRequest, TaskResponse
from domain.entities.task import Task, Priority, Status
from domain.exceptions import TaskNotFoundError, InvalidTaskError
from domain.repositories.task_repository import TaskRepository


class CreateTask:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, request: CreateTaskRequest) -> TaskResponse:
        if not request.title.strip():
            raise InvalidTaskError("Task title cannot be empty.")
        try:
            priority = Priority(request.priority.lower())
        except ValueError:
            raise InvalidTaskError(f"Invalid priority '{request.priority}'. Choose: low, medium, high.")
        task = Task(title=request.title.strip(), description=request.description, priority=priority)
        return TaskResponse.from_task(self._repo.save(task))


class ListTasks:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, status_filter: str = None, priority_filter: str = None) -> List[TaskResponse]:
        if status_filter:
            try:
                status = Status(status_filter.lower())
            except ValueError:
                raise InvalidTaskError(f"Invalid status '{status_filter}'.")
            tasks = self._repo.find_by_status(status)
        elif priority_filter:
            try:
                priority = Priority(priority_filter.lower())
            except ValueError:
                raise InvalidTaskError(f"Invalid priority '{priority_filter}'.")
            tasks = self._repo.find_by_priority(priority)
        else:
            tasks = self._repo.find_all()
        return [TaskResponse.from_task(t) for t in tasks]


class CompleteTask:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, task_id: str) -> TaskResponse:
        task = self._repo.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        task.complete()
        return TaskResponse.from_task(self._repo.save(task))


class StartTask:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, task_id: str) -> TaskResponse:
        task = self._repo.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        task.start()
        return TaskResponse.from_task(self._repo.save(task))


class DeleteTask:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, task_id: str) -> bool:
        task = self._repo.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return self._repo.delete(task_id)


class GetTask:
    def __init__(self, repository: TaskRepository):
        self._repo = repository

    def execute(self, task_id: str) -> TaskResponse:
        task = self._repo.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return TaskResponse.from_task(task)
