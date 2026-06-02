import pytest
from datetime import datetime
from domain.entities.task import Task, Priority, Status


class TestTaskCreation:
    def test_creates_task_with_defaults(self):
        task = Task(title="Write tests")
        assert task.title == "Write tests"
        assert task.status == Status.PENDING
        assert task.priority == Priority.MEDIUM

    def test_each_task_gets_unique_id(self):
        t1, t2 = Task(title="A"), Task(title="B")
        assert t1.id != t2.id

    def test_created_at_is_set_on_init(self):
        before = datetime.utcnow()
        task = Task(title="Timed task")
        after = datetime.utcnow()
        assert before <= task.created_at <= after


class TestTaskTransitions:
    def test_complete_changes_status_to_done(self):
        task = Task(title="Finish report")
        task.complete()
        assert task.status == Status.DONE

    def test_start_changes_status_to_in_progress(self):
        task = Task(title="Begin work")
        task.start()
        assert task.status == Status.IN_PROGRESS

    def test_cannot_complete_an_already_done_task(self):
        task = Task(title="One-shot")
        task.complete()
        with pytest.raises(ValueError, match="already completed"):
            task.complete()

    def test_cannot_start_a_done_task(self):
        task = Task(title="No restart")
        task.complete()
        with pytest.raises(ValueError, match="already completed"):
            task.start()

    def test_can_complete_an_in_progress_task(self):
        task = Task(title="In flight")
        task.start()
        task.complete()
        assert task.status == Status.DONE


class TestTaskUpdate:
    def test_update_title(self):
        task = Task(title="Old title")
        task.update_title("New title")
        assert task.title == "New title"

    def test_update_title_strips_whitespace(self):
        task = Task(title="Title")
        task.update_title("  Trimmed  ")
        assert task.title == "Trimmed"

    def test_update_title_rejects_empty(self):
        task = Task(title="Valid")
        with pytest.raises(ValueError, match="cannot be empty"):
            task.update_title("   ")


class TestTaskPriority:
    def test_is_high_priority_true_for_high(self):
        assert Task(title="Urgent", priority=Priority.HIGH).is_high_priority() is True

    def test_is_high_priority_false_for_medium(self):
        assert Task(title="Normal", priority=Priority.MEDIUM).is_high_priority() is False
