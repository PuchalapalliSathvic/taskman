import pytest
from typing import List, Optional
from domain.entities.task import Task, Priority, Status
from domain.repositories.task_repository import TaskRepository
from domain.exceptions import TaskNotFoundError, InvalidTaskError
from application.dtos import CreateTaskRequest
from application.use_cases.task_use_cases import (
    CreateTask, ListTasks, CompleteTask, StartTask, DeleteTask, GetTask,
)


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._store = {}

    def save(self, task):
        self._store[task.id] = task
        return task

    def find_by_id(self, task_id):
        for key, task in self._store.items():
            if key == task_id or key.startswith(task_id):
                return task
        return None

    def find_all(self):
        return list(self._store.values())

    def find_by_status(self, status):
        return [t for t in self._store.values() if t.status == status]

    def find_by_priority(self, priority):
        return [t for t in self._store.values() if t.priority == priority]

    def delete(self, task_id):
        for key in list(self._store.keys()):
            if key == task_id or key.startswith(task_id):
                del self._store[key]
                return True
        return False


@pytest.fixture
def repo():
    return InMemoryTaskRepository()


class TestCreateTask:
    def test_creates_and_returns_task(self, repo):
        result = CreateTask(repo).execute(CreateTaskRequest(title="Buy milk", priority="high"))
        assert result.title == "Buy milk"
        assert result.priority == "high"
        assert result.status == "pending"

    def test_persists_task_to_repo(self, repo):
        result = CreateTask(repo).execute(CreateTaskRequest(title="Saved task"))
        assert repo.find_by_id(result.id) is not None

    def test_rejects_empty_title(self, repo):
        with pytest.raises(InvalidTaskError, match="cannot be empty"):
            CreateTask(repo).execute(CreateTaskRequest(title="   "))

    def test_rejects_invalid_priority(self, repo):
        with pytest.raises(InvalidTaskError, match="Invalid priority"):
            CreateTask(repo).execute(CreateTaskRequest(title="Task", priority="urgent"))

    def test_default_priority_is_medium(self, repo):
        result = CreateTask(repo).execute(CreateTaskRequest(title="Default"))
        assert result.priority == "medium"


class TestListTasks:
    def test_lists_all_tasks(self, repo):
        for i in range(3):
            CreateTask(repo).execute(CreateTaskRequest(title=f"Task {i}"))
        assert len(ListTasks(repo).execute()) == 3

    def test_returns_empty_list(self, repo):
        assert ListTasks(repo).execute() == []

    def test_filters_by_status(self, repo):
        t = CreateTask(repo).execute(CreateTaskRequest(title="Active"))
        CompleteTask(repo).execute(t.id)
        CreateTask(repo).execute(CreateTaskRequest(title="Pending"))
        done = ListTasks(repo).execute(status_filter="done")
        assert len(done) == 1 and done[0].title == "Active"

    def test_filters_by_priority(self, repo):
        CreateTask(repo).execute(CreateTaskRequest(title="Urgent", priority="high"))
        CreateTask(repo).execute(CreateTaskRequest(title="Normal", priority="medium"))
        high = ListTasks(repo).execute(priority_filter="high")
        assert len(high) == 1 and high[0].title == "Urgent"


class TestCompleteTask:
    def test_marks_task_done(self, repo):
        task = CreateTask(repo).execute(CreateTaskRequest(title="Finish me"))
        assert CompleteTask(repo).execute(task.id).status == "done"

    def test_raises_if_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            CompleteTask(repo).execute("nonexistent")

    def test_raises_if_already_done(self, repo):
        task = CreateTask(repo).execute(CreateTaskRequest(title="Oops"))
        CompleteTask(repo).execute(task.id)
        with pytest.raises(ValueError):
            CompleteTask(repo).execute(task.id)


class TestStartTask:
    def test_marks_task_in_progress(self, repo):
        task = CreateTask(repo).execute(CreateTaskRequest(title="Begin"))
        assert StartTask(repo).execute(task.id).status == "in_progress"

    def test_raises_if_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            StartTask(repo).execute("ghost")


class TestDeleteTask:
    def test_deletes_existing_task(self, repo):
        task = CreateTask(repo).execute(CreateTaskRequest(title="Delete me"))
        DeleteTask(repo).execute(task.id)
        assert repo.find_by_id(task.id) is None

    def test_raises_if_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            DeleteTask(repo).execute("ghost")


class TestGetTask:
    def test_returns_task_by_id(self, repo):
        created = CreateTask(repo).execute(CreateTaskRequest(title="Find me"))
        result = GetTask(repo).execute(created.id)
        assert result.title == "Find me"

    def test_raises_if_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            GetTask(repo).execute("missing")
