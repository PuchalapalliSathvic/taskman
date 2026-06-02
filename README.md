# taskman — Clean Architecture CLI Task Manager

## My Approach

My first step was to understand Clean Architecture before writing any code. The core principle that guided my entire design was simple: business rules should never depend on infrastructure details. The database, the file system, the CLI — these are just delivery mechanisms. The real logic should be completely independent of them.

I chose a task manager as my utility because it has enough real business rules to properly demonstrate the architecture — a task cannot be completed twice, titles cannot be empty, status transitions must be controlled — without becoming so complex that the architecture gets buried under feature code.

## How I Structured It

I identified three natural boundaries and built around them.

The domain layer is the core. It contains the Task entity and all its rules. This layer has zero external dependencies — no file system, no libraries, nothing. Just pure Python business logic.

The application layer contains the use cases — one class per user action. CreateTask, ListTasks, CompleteTask, StartTask, DeleteTask, GetTask. Each use case receives a repository through its constructor, talks to the domain, and returns a clean response. It never touches a file or prints anything.

The infrastructure layer is where the real world enters. The JSON file repository lives here. The CLI lives here. These are the only places where I/O happens. Swapping JSON for a database would mean writing one new class and changing one line in main.py — nothing else would change.

The key decision was the repository interface. The domain defines what storage must be able to do. Infrastructure implements it. This means use cases depend on an abstraction they own, not on any concrete implementation. For testing, I simply wrote an InMemoryTaskRepository — a plain Python dictionary satisfying the same contract. No mocking frameworks needed.

## Project Structure

    taskman/
    ├── domain/
    │   ├── entities/task.py           Task entity with all business rules
    │   ├── repositories/              Abstract repository interface
    │   └── exceptions.py             Domain-specific exceptions
    ├── application/
    │   ├── use_cases/                 One use case class per user action
    │   └── dtos.py                    Request and response data objects
    ├── infrastructure/
    │   ├── persistence/               JSON file adapter
    │   └── cli/                       Terminal presentation layer
    ├── tests/
    │   ├── domain/                    Pure unit tests, zero I/O
    │   ├── application/               Use case tests with in-memory fake
    │   └── infrastructure/            File system integration tests
    └── main.py                        Entry point and dependency wiring

## Setup

Requires Python 3.10 or higher. No third-party runtime dependencies.

    git clone https://github.com/PuchalapalliSathvic/taskman.git
    cd taskman
    pip install pytest pytest-cov

## Usage

    python main.py add "Deploy to production" -p high -d "Blue-green deployment"
    python main.py add "Write documentation"
    python main.py list
    python main.py list --status pending
    python main.py list --status done
    python main.py list --priority high
    python main.py show <task-id>
    python main.py start <task-id>
    python main.py complete <task-id>
    python main.py delete <task-id>

Task IDs are full UUIDs but the CLI accepts the first 8 characters for convenience.
Tasks are stored at ~/.taskman/tasks.json and persist across sessions.

## Running Tests

    python -m pytest tests/ -v
    python -m pytest tests/ -v --cov=domain --cov=application --cov-report=term-missing

Three test suites, each targeting a different layer:

- Domain tests: pure business rule validation, no I/O whatsoever
- Application tests: use cases exercised through an in-memory repository
- Infrastructure tests: JSON repository tested against real temporary files

41 tests, all passing.
