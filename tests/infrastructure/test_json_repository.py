import pytest
from domain.entities.task import Task, Priority, Status
from infrastructure.persistence.json_task_repository import JsonFileTaskRepository


@pytest.fixture
def repo(tmp_path):
    return JsonFileTaskRepository(filepath=str(tmp_path / "test_tasks.json"))


class TestJsonFileTaskRepository:
    def test_save_and_find_by_id(self, repo):
        task = Task(title="Persisted task", priority=Priority.HIGH)
        repo.save(task)
        found = repo.find_by_id(task.id)
        assert found is not None and found.title == "Persisted task"

    def test_find_by_short_id(self, repo):
        task = Task(title="Short ID lookup")
        repo.save(task)
        assert repo.find_by_id(task.id[:8]) is not None

    def test_find_by_id_returns_none_if_missing(self, repo):
        assert repo.find_by_id("nonexistent") is None

    def test_find_all_returns_all_tasks(self, repo):
        for i in range(4):
            repo.save(Task(title=f"Task {i}"))
        assert len(repo.find_all()) == 4

    def test_find_all_empty(self, repo):
        assert repo.find_all() == []

    def test_update_existing_task(self, repo):
        task = Task(title="Original")
        repo.save(task)
        task.update_title("Updated")
        repo.save(task)
        assert repo.find_by_id(task.id).title == "Updated"

    def test_find_by_status(self, repo):
        t1 = Task(title="Pending task")
        t2 = Task(title="Done task")
        t2.complete()
        repo.save(t1); repo.save(t2)
        done = repo.find_by_status(Status.DONE)
        assert len(done) == 1 and done[0].title == "Done task"

    def test_find_by_priority(self, repo):
        repo.save(Task(title="High", priority=Priority.HIGH))
        repo.save(Task(title="Low", priority=Priority.LOW))
        assert len(repo.find_by_priority(Priority.HIGH)) == 1

    def test_delete_removes_task(self, repo):
        task = Task(title="To delete")
        repo.save(task)
        assert repo.delete(task.id) is True
        assert repo.find_by_id(task.id) is None

    def test_data_persists_across_instances(self, tmp_path):
        filepath = str(tmp_path / "shared.json")
        repo1 = JsonFileTaskRepository(filepath=filepath)
        task = Task(title="Cross-instance task")
        repo1.save(task)
        repo2 = JsonFileTaskRepository(filepath=filepath)
        assert repo2.find_by_id(task.id).title == "Cross-instance task"
