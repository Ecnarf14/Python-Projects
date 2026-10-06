"""VA Task Manager - a command-line to-do app.

Features: saves tasks to a file, priorities, due dates, edit, multi-select
complete/uncomplete/delete, overdue warnings, and CSV export.
"""
import csv
import json
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path("tasks.json")
PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}


# ---------- Saving and loading ----------
def load_tasks():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("⚠ tasks.json is damaged. Starting with an empty list.")
    return []


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


# ---------- Helpers (written once, reused everywhere) ----------
def show_tasks(tasks):
    """Print all tasks. Used by every menu option that needs the list."""
    print("\nYour tasks:")
    if not tasks:
        print("No tasks available.")
        return
    today = date.today().isoformat()
    for number, task in enumerate(tasks, 1):
        mark = "✓" if task["completed"] else "☐"
        line = f"{number}. {mark} {task['name']}  [{task['priority']}]"
        if task["due"]:
            line += f"  due {task['due']}"
            if task["due"] < today and not task["completed"]:
                line += "  ⚠ OVERDUE"
        print(line)


def parse_numbers(text, total):
    """Turn '1, 3, x, 9' into (valid_numbers, problems)."""
    valid, problems = [], []
    for part in text.split(","):
        part = part.strip()
        if not part.isdigit():
            problems.append(f"'{part}' is not a valid task number.")
        elif not 1 <= int(part) <= total:
            problems.append(f"Task {part} does not exist.")
        else:
            valid.append(int(part))
    return sorted(set(valid)), problems


def ask_due_date():
    """Ask until the user types a valid date (YYYY-MM-DD) or leaves it blank."""
    while True:
        text = input("Due date (YYYY-MM-DD, or press Enter to skip): ").strip()
        if not text:
            return ""
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("❌ Please use the format YYYY-MM-DD, for example 2026-10-30.")


def ask_priority():
    while True:
        choice = input("Priority (1=High, 2=Medium, 3=Low) [2]: ").strip() or "2"
        if choice in PRIORITIES:
            return PRIORITIES[choice]
        print("❌ Please enter 1, 2, or 3.")


# ---------- Menu actions ----------
def add_task(tasks):
    name = input("Enter a task: ").strip()
    if not name:
        print("❌ Task name cannot be empty.")
        return
    tasks.append({
        "name": name,
        "completed": False,
        "priority": ask_priority(),
        "due": ask_due_date(),
    })
    print("Task added!")


def edit_task(tasks):
    if not tasks:
        print("There are no tasks to edit.")
        return
    show_tasks(tasks)
    valid, problems = parse_numbers(input("\nTask number to edit: "), len(tasks))
    if len(valid) != 1:
        print("❌", problems[0] if problems else "Please enter one task number.")
        return
    task = tasks[valid[0] - 1]
    new_name = input(f"New name [{task['name']}]: ").strip()
    if new_name:
        task["name"] = new_name
    task["priority"] = ask_priority()
    task["due"] = ask_due_date()
    print("Task updated!")


def set_completed(tasks, completed):
    """One function replaces the two nearly identical blocks (options 4 and 6)."""
    if not tasks:
        print("There are no tasks to update.")
        return
    show_tasks(tasks)
    word = "complete" if completed else "uncheck"
    text = input(f"\nEnter task numbers to {word} (example: 1,3,4): ")
    valid, problems = parse_numbers(text, len(tasks))
    for number in valid:
        tasks[number - 1]["completed"] = completed
        state = "completed" if completed else "NOT completed"
        print(f"✓ Task {number} marked as {state}.")
    for problem in problems:
        print("❌", problem)


def delete_tasks(tasks):
    if not tasks:
        print("There are no tasks to delete.")
        return
    show_tasks(tasks)
    text = input("\nEnter task numbers to delete (example: 1,3): ")
    valid, problems = parse_numbers(text, len(tasks))
    for number in reversed(valid):  # delete from the end so numbers don't shift
        removed = tasks.pop(number - 1)
        print(f"Task deleted: {removed['name']}")
    for problem in problems:
        print("❌", problem)


def clear_completed(tasks):
    before = len(tasks)
    tasks[:] = [t for t in tasks if not t["completed"]]
    print(f"Removed {before - len(tasks)} completed task(s).")


def export_csv(tasks):
    if not tasks:
        print("There are no tasks to export.")
        return
    with open("tasks_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "completed", "priority", "due"])
        writer.writeheader()
        writer.writerows(tasks)
    print("Exported to tasks_export.csv (opens in Excel).")


# ---------- Main program ----------
MENU = """
--- VA TASK MANAGER ---
1. Add task
2. View tasks
3. Edit task
4. Mark task(s) as completed
5. Mark task(s) as not completed
6. Delete task(s)
7. Clear all completed tasks
8. Export to CSV
9. Exit"""


def main():
    tasks = load_tasks()
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            edit_task(tasks)
        elif choice == "4":
            set_completed(tasks, True)
        elif choice == "5":
            set_completed(tasks, False)
        elif choice == "6":
            delete_tasks(tasks)
        elif choice == "7":
            clear_completed(tasks)
        elif choice == "8":
            export_csv(tasks)
        elif choice == "9":
            save_tasks(tasks)
            print("Tasks saved. Goodbye!")
            break
        else:
            print("❌ Invalid choice.")
            continue

        save_tasks(tasks)  # save after every change so nothing is lost


if __name__ == "__main__":
    main() 