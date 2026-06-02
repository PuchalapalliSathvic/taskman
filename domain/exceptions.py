class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        super().__init__(f"Task with id '{task_id}' was not found.")
        self.task_id = task_id


class TaskAlreadyCompletedError(Exception):
    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' is already completed.")
        self.task_id = task_id


class InvalidTaskError(Exception):
    pass
