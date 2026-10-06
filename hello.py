tasks = []

while True:
    print("\n--- VA TASK MANAGER ---")
    print("1. Add task")
    print("2. View tasks")
    print("3. Delete task")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        task = input("Enter a task: ")
        tasks.append(task)
        print("Task added!")

    elif choice == "2":
        print("\nYour tasks:")

        if not tasks:
            print("No tasks available.")
        else:
            for number, task in enumerate(tasks, 1):
                print(f"{number}. {task}")

    elif choice == "3":
        if not tasks:
            print("There are no tasks to delete.")
        else:
            print("\nYour tasks:")

            for number, task in enumerate(tasks, 1):
                print(f"{number}. {task}")

            task_number = int(input("Enter the task number to delete: "))

            if 1 <= task_number <= len(tasks):
                deleted_task = tasks.pop(task_number - 1)
                print(f"Task deleted: {deleted_task}")
            else:
                print("Invalid task number.")

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice.")
