import argparse
import sys

from application.dtos import CreateTaskRequest
from application.use_cases.task_use_cases import (
    CreateTask, ListTasks, CompleteTask, StartTask, DeleteTask, GetTask,
)
from domain.exceptions import TaskNotFoundError, InvalidTaskError
from infrastructure.persistence.json_task_repository import JsonFileTaskRepository

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"

STATUS_COLOUR  = {"pending": YELLOW, "in_progress": CYAN, "done": GREEN}
PRIORITY_COLOUR = {"low": DIM, "medium": RESET, "high": RED + BOLD}

def _fmt_status(s):   return f"{STATUS_COLOUR.get(s, '')}{s}{RESET}"
def _fmt_priority(p): return f"{PRIORITY_COLOUR.get(p, '')}{p}{RESET}"

def _print_header():
    print(f"\n  {'ID':<10}{'TITLE':<40}{'STATUS':<12}{'PRIORITY':<10}{'CREATED'}")
    print("  " + "─" * 80)

def _print_task(t):
    print(f"  {BOLD}{t.id[:8]}{RESET}  {t.title:<40} {_fmt_status(t.status):<20} {_fmt_priority(t.priority):<12} {DIM}{t.created_at[:10]}{RESET}")

def cmd_add(args, repo):
    try:
        task = CreateTask(repo).execute(CreateTaskRequest(title=args.title, description=args.description or "", priority=args.priority))
        print(f"\n{GREEN}✔ Task created{RESET}")
        print(f"  ID       : {BOLD}{task.id[:8]}{RESET}")
        print(f"  Title    : {task.title}")
        print(f"  Priority : {_fmt_priority(task.priority)}")
        print(f"  Status   : {_fmt_status(task.status)}\n")
    except InvalidTaskError as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)

def cmd_list(args, repo):
    try:
        tasks = ListTasks(repo).execute(status_filter=args.status, priority_filter=args.priority)
    except InvalidTaskError as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)
    if not tasks:
        print(f"\n{DIM}No tasks found.{RESET}\n"); return
    _print_header()
    for t in tasks: _print_task(t)
    print(f"\n  {DIM}{len(tasks)} task(s){RESET}\n")

def cmd_show(args, repo):
    try:
        t = GetTask(repo).execute(args.id)
        print(f"\n  {BOLD}Task {t.id[:8]}{RESET}")
        print(f"  {'Title':<12}: {t.title}")
        print(f"  {'Description':<12}: {t.description or DIM + '(none)' + RESET}")
        print(f"  {'Priority':<12}: {_fmt_priority(t.priority)}")
        print(f"  {'Status':<12}: {_fmt_status(t.status)}")
        print(f"  {'Created':<12}: {t.created_at}\n")
    except TaskNotFoundError as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)

def cmd_start(args, repo):
    try:
        task = StartTask(repo).execute(args.id)
        print(f"\n{CYAN}→ Task started{RESET}: {task.title} [{task.id[:8]}]\n")
    except (TaskNotFoundError, ValueError) as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)

def cmd_complete(args, repo):
    try:
        task = CompleteTask(repo).execute(args.id)
        print(f"\n{GREEN}✔ Task completed{RESET}: {task.title} [{task.id[:8]}]\n")
    except (TaskNotFoundError, ValueError) as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)

def cmd_delete(args, repo):
    try:
        DeleteTask(repo).execute(args.id)
        print(f"\n{RED}✗ Task deleted{RESET}: [{args.id}]\n")
    except TaskNotFoundError as e:
        print(f"{RED}Error: {e}{RESET}", file=sys.stderr); sys.exit(1)

def build_parser():
    parser = argparse.ArgumentParser(prog="taskman", description="Clean architecture task manager CLI.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add", help="Create a new task")
    p_add.add_argument("title")
    p_add.add_argument("-d", "--description")
    p_add.add_argument("-p", "--priority", default="medium", choices=["low", "medium", "high"])
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--status", choices=["pending", "in_progress", "done"])
    p_list.add_argument("--priority", choices=["low", "medium", "high"])
    p_show = sub.add_parser("show", help="Show task details")
    p_show.add_argument("id")
    p_start = sub.add_parser("start", help="Mark task as in progress")
    p_start.add_argument("id")
    p_done = sub.add_parser("complete", help="Mark task as done")
    p_done.add_argument("id")
    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("id")
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    repo = JsonFileTaskRepository()
    dispatch = {"add": cmd_add, "list": cmd_list, "show": cmd_show, "start": cmd_start, "complete": cmd_complete, "delete": cmd_delete}
    dispatch[args.command](args, repo)
