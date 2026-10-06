import json
import os
from datetime import datetime, date


# ==========================================
# VA TASK MANAGER
# ==========================================

DATA_FILE = "tasks.json"


# ==========================================
# DATA MANAGEMENT
# ==========================================

def load_data():
    """Load tasks and activity history from JSON file."""

    if not os.path.exists(DATA_FILE):
        return {
            "tasks": [],
            "history": []
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except (json.JSONDecodeError, OSError):
        print("⚠ Could not load saved data.")
        return {
            "tasks": [],
            "history": []
        }


def save_data():
    """Automatically save tasks and history."""

    data = {
        "tasks": tasks,
        "history": history
    }

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    except OSError:
        print("❌ Could not save data.")


# ==========================================
# ACTIVITY HISTORY
# ==========================================

def add_history(message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history.append({
        "timestamp": timestamp,
        "message": message
    })

    save_data()


# ==========================================
# DISPLAY HEADER
# ==========================================

def show_header():

    print("\n" + "=" * 70)
    print("                    VA TASK MANAGER")
    print("=" * 70)


# ==========================================
# GET TASK STATUS
# ==========================================

def get_status(task):

    if task["completed"]:
        return "COMPLETED"

    due_date = datetime.strptime(
        task["due_date"],
        "%Y-%m-%d"
    ).date()

    today = date.today()

    if due_date < today:
        return "OVERDUE"

    return "PENDING"


# ==========================================
# DISPLAY TASKS
# ==========================================

def display_tasks(task_list=None):

    if task_list is None:
        task_list = tasks

    if not task_list:
        print("\nNo tasks available.")
        return

    print("\n" + "-" * 70)

    for number, task in enumerate(task_list, 1):

        status = get_status(task)

        if status == "COMPLETED":
            status_icon = "✓"
        elif status == "OVERDUE":
            status_icon = "🔴"
        else:
            status_icon = "🟡"

        print(
            f"{number}. {status_icon} {task['name']}"
        )

        print(
            f"   Client: {task['client']}"
        )

        print(
            f"   Due: {task['due_date']}"
        )

        print(
            f"   Priority: {task['priority']}"
        )

        print(
            f"   Status: {status}"
        )

        print("-" * 70)


# ==========================================
# ADD TASK
# ==========================================

def add_task():

    print("\n--- ADD TASK ---")

    task_name = input(
        "Task name: "
    ).strip()

    if not task_name:
        print("❌ Task name cannot be empty.")
        return

    client = input(
        "Client name: "
    ).strip()

    if not client:
        print("❌ Client name cannot be empty.")
        return

    # Priority
    print("\nPriority:")
    print("1. Low")
    print("2. Medium")
    print("3. High")

    priority_choice = input(
        "Choose priority: "
    ).strip()

    priority_options = {
        "1": "Low",
        "2": "Medium",
        "3": "High"
    }

    if priority_choice not in priority_options:
        print("❌ Invalid priority.")
        return

    priority = priority_options[priority_choice]

    # Due date
    while True:

        due_date = input(
            "Due date (YYYY-MM-DD): "
        ).strip()

        try:

            datetime.strptime(
                due_date,
                "%Y-%m-%d"
            )

            break

        except ValueError:

            print(
                "❌ Invalid date. "
                "Please use YYYY-MM-DD."
            )

    new_task = {
        "name": task_name,
        "client": client,
        "due_date": due_date,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    tasks.append(new_task)

    save_data()

    add_history(
        f"Created task '{task_name}' "
        f"for client '{client}'."
    )

    print(
        f"\n✓ Task '{task_name}' added successfully."
    )


# ==========================================
# SELECT TASK NUMBERS
# ==========================================

def get_selected_numbers():

    user_input = input(
        "\nEnter task numbers "
        "(example: 1,3,5): "
    ).strip()

    if not user_input:
        print("❌ No task numbers entered.")
        return []

    selected_numbers = user_input.split(",")

    valid_numbers = []

    for number in selected_numbers:

        number = number.strip()

        if not number.isdigit():

            print(
                f"❌ '{number}' "
                f"is not a valid task number."
            )

            continue

        task_number = int(number)

        if 1 <= task_number <= len(tasks):

            if task_number not in valid_numbers:
                valid_numbers.append(task_number)

        else:

            print(
                f"❌ Task {task_number} "
                f"does not exist."
            )

    return valid_numbers


# ==========================================
# MARK TASKS COMPLETED
# ==========================================

def complete_tasks():

    if not tasks:
        print("\n❌ There are no tasks.")
        return

    display_tasks()

    selected_numbers = get_selected_numbers()

    if not selected_numbers:
        return

    for number in selected_numbers:

        task = tasks[number - 1]

        if task["completed"]:

            print(
                f"ℹ Task {number} "
                f"is already completed."
            )

        else:

            task["completed"] = True

            print(
                f"✓ Completed: {task['name']}"
            )

            add_history(
                f"Completed task '{task['name']}'."
            )

    save_data()


# ==========================================
# UNDO COMPLETED TASKS
# ==========================================

def undo_tasks():

    if not tasks:
        print("\n❌ There are no tasks.")
        return

    display_tasks()

    selected_numbers = get_selected_numbers()

    if not selected_numbers:
        return

    for number in selected_numbers:

        task = tasks[number - 1]

        if not task["completed"]:

            print(
                f"ℹ Task {number} "
                f"is already pending."
            )

        else:

            task["completed"] = False

            print(
                f"↩ Restored: {task['name']}"
            )

            add_history(
                f"Marked task '{task['name']}' "
                f"as pending."
            )

    save_data()


# ==========================================
# DELETE TASKS
# ==========================================

def delete_tasks():

    if not tasks:
        print("\n❌ There are no tasks.")
        return

    display_tasks()

    selected_numbers = get_selected_numbers()

    if not selected_numbers:
        return

    print("\nTasks selected for deletion:")

    for number in selected_numbers:

        print(
            f"- {tasks[number - 1]['name']}"
        )

    confirmation = input(
        "\nAre you sure? (y/n): "
    ).lower().strip()

    if confirmation != "y":

        print("Deletion cancelled.")
        return

    for number in sorted(
        selected_numbers,
        reverse=True
    ):

        deleted_task = tasks.pop(number - 1)

        print(
            f"✓ Deleted: "
            f"{deleted_task['name']}"
        )

        add_history(
            f"Deleted task "
            f"'{deleted_task['name']}'."
        )

    save_data()


# ==========================================
# SEARCH TASKS
# ==========================================

def search_tasks():

    if not tasks:
        print("\n❌ There are no tasks.")
        return

    keyword = input(
        "\nSearch by task or client: "
    ).strip().lower()

    if not keyword:
        print("❌ Search cannot be empty.")
        return

    results = []

    for task in tasks:

        if (
            keyword in task["name"].lower()
            or keyword in task["client"].lower()
        ):

            results.append(task)

    if not results:

        print(
            f"\n❌ No results found for "
            f"'{keyword}'."
        )

        return

    print(
        f"\n🔍 Search results for '{keyword}':"
    )

    display_tasks(results)


# ==========================================
# FILTER BY STATUS
# ==========================================

def filter_tasks():

    if not tasks:
        print("\n❌ There are no tasks.")
        return

    print("\n--- FILTER TASKS ---")
    print("1. Pending")
    print("2. Completed")
    print("3. Overdue")
    print("4. High Priority")

    choice = input(
        "Choose filter: "
    ).strip()

    results = []

    for task in tasks:

        status = get_status(task)

        if choice == "1" and status == "PENDING":
            results.append(task)

        elif choice == "2" and status == "COMPLETED":
            results.append(task)

        elif choice == "3" and status == "OVERDUE":
            results.append(task)

        elif choice == "4" and task["priority"] == "High":
            results.append(task)

    if not results:

        print("\nNo tasks match this filter.")
        return

    display_tasks(results)


# ==========================================
# TASK STATISTICS
# ==========================================

def show_statistics():

    total = len(tasks)

    completed = 0
    pending = 0
    overdue = 0
    high_priority = 0

    for task in tasks:

        status = get_status(task)

        if status == "COMPLETED":
            completed += 1

        elif status == "PENDING":
            pending += 1

        elif status == "OVERDUE":
            overdue += 1

        if task["priority"] == "High":
            high_priority += 1

    print("\n" + "=" * 45)
    print("              TASK STATISTICS")
    print("=" * 45)

    print(f"Total tasks:       {total}")
    print(f"Completed:         {completed}")
    print(f"Pending:           {pending}")
    print(f"Overdue:           {overdue}")
    print(f"High priority:     {high_priority}")

    if total > 0:

        completion_rate = (
            completed / total
        ) * 100

        print(
            f"Completion rate:   "
            f"{completion_rate:.1f}%"
        )

    print("=" * 45)


# ==========================================
# ACTIVITY HISTORY
# ==========================================

def show_history():

    if not history:

        print(
            "\nNo activity history available."
        )

        return

    print("\n" + "=" * 70)
    print("                 ACTIVITY HISTORY")
    print("=" * 70)

    for item in reversed(history):

        print(
            f"{item['timestamp']} | "
            f"{item['message']}"
        )

    print("=" * 70)


# ==========================================
# MAIN MENU
# ==========================================

def main():

    global tasks
    global history

    data = load_data()

    tasks = data.get("tasks", [])
    history = data.get("history", [])

    print("\n✓ VA Task Manager started.")

    print(
        f"✓ Loaded {len(tasks)} saved task(s)."
    )

    while True:

        show_header()

        print("""
1. Add Task
2. View Tasks
3. Delete Tasks
4. Mark Tasks as Completed
5. Undo Completed Tasks
6. Search Tasks
7. Filter Tasks
8. Task Statistics
9. Activity History
10. Exit
""")

        choice = input(
            "Choose an option: "
        ).strip()

        if choice == "1":

            add_task()

        elif choice == "2":

            display_tasks()

        elif choice == "3":

            delete_tasks()

        elif choice == "4":

            complete_tasks()

        elif choice == "5":

            undo_tasks()

        elif choice == "6":

            search_tasks()

        elif choice == "7":

            filter_tasks()

        elif choice == "8":

            show_statistics()

        elif choice == "9":

            show_history()

        elif choice == "10":

            save_data()

            print(
                "\n✓ All data saved."
            )

            print(
                "Thank you for using "
                "VA Task Manager! 👋"
            )

            break

        else:

            print(
                "\n❌ Invalid choice. "
                "Please choose 1-10."
            )


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
