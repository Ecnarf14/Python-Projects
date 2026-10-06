import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

# ==========================================
# VA TASK MANAGER - DESKTOP VERSION (tkinter)
# ==========================================

# Save tasks.json next to the script (or next to the .exe once packaged)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "tasks.json")
DATE_FORMAT = "%Y-%m-%d"


# ==========================================
# DATA MANAGEMENT
# ==========================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return [], []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tasks", []), data.get("history", [])
    except (json.JSONDecodeError, OSError):
        messagebox.showwarning("Load error", "Could not load saved data.")
        return [], []


def get_status(task):
    if task["completed"]:
        return "COMPLETED"
    due = datetime.strptime(task["due_date"], DATE_FORMAT).date()
    return "OVERDUE" if due < date.today() else "PENDING"


# ==========================================
# APPLICATION
# ==========================================

class TaskManagerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("VA Task Manager")
        self.geometry("1000x640")
        self.minsize(880, 540)

        self.tasks, self.history = load_data()

        self.build_ui()
        self.refresh()

    # ---------- saving / history ----------

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"tasks": self.tasks, "history": self.history}, f, indent=4)
        except OSError:
            messagebox.showerror("Save error", "Could not save data.")

    def add_history(self, message):
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        })

    # ---------- UI ----------

    def build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tasks_tab = ttk.Frame(notebook)
        self.stats_tab = ttk.Frame(notebook)
        self.history_tab = ttk.Frame(notebook)
        notebook.add(self.tasks_tab, text="  Tasks  ")
        notebook.add(self.stats_tab, text="  Statistics  ")
        notebook.add(self.history_tab, text="  Activity History  ")

        self.build_tasks_tab()
        self.build_stats_tab()
        self.build_history_tab()

    def build_tasks_tab(self):
        # ----- Add task form -----
        form = ttk.LabelFrame(self.tasks_tab, text="Add Task")
        form.pack(fill="x", padx=6, pady=6)

        self.name_var = tk.StringVar()
        self.client_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Medium")
        self.due_var = tk.StringVar(value=date.today().strftime(DATE_FORMAT))

        ttk.Label(form, text="Task:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Client:").grid(row=0, column=2, padx=6, sticky="e")
        ttk.Entry(form, textvariable=self.client_var, width=20).grid(row=0, column=3, padx=4)

        ttk.Label(form, text="Priority:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        ttk.Combobox(
            form, textvariable=self.priority_var, state="readonly",
            values=["Low", "Medium", "High"], width=12
        ).grid(row=1, column=1, padx=4, sticky="w")

        ttk.Label(form, text="Due (YYYY-MM-DD):").grid(row=1, column=2, padx=6, sticky="e")
        ttk.Entry(form, textvariable=self.due_var, width=14).grid(row=1, column=3, padx=4, sticky="w")

        ttk.Button(form, text="➕ Add Task", command=self.add_task).grid(
            row=0, column=4, rowspan=2, padx=12, ipadx=8, ipady=6
        )

        # ----- Search / filter bar -----
        bar = ttk.Frame(self.tasks_tab)
        bar.pack(fill="x", padx=6, pady=(4, 0))

        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(bar, textvariable=self.search_var, width=28).pack(side="left", padx=6)

        ttk.Label(bar, text="Filter:").pack(side="left", padx=(16, 0))
        self.filter_var = tk.StringVar(value="All")
        filter_box = ttk.Combobox(
            bar, textvariable=self.filter_var, state="readonly", width=16,
            values=["All", "Pending", "Completed", "Overdue", "High Priority"]
        )
        filter_box.pack(side="left", padx=6)
        filter_box.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        # ----- Task table -----
        table_frame = ttk.Frame(self.tasks_tab)
        table_frame.pack(fill="both", expand=True, padx=6, pady=6)

        columns = ("name", "client", "due", "priority", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        headings = {
            "name": ("Task", 300), "client": ("Client", 180),
            "due": ("Due Date", 110), "priority": ("Priority", 90), "status": ("Status", 110),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("OVERDUE", foreground="#c0392b")
        self.tree.tag_configure("COMPLETED", foreground="#7f8c8d")
        self.tree.tag_configure("PENDING", foreground="#000000")

        self.tree.bind("<Double-1>", lambda _e: self.toggle_selected())
        self.tree.bind("<Delete>", lambda _e: self.delete_selected())

        # ----- Action buttons -----
        actions = ttk.Frame(self.tasks_tab)
        actions.pack(fill="x", padx=6, pady=(0, 8))

        ttk.Button(actions, text="✓ Mark Completed", command=self.complete_selected).pack(side="left", padx=4)
        ttk.Button(actions, text="↩ Undo Completed", command=self.undo_selected).pack(side="left", padx=4)
        ttk.Button(actions, text="🗑 Delete", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Label(actions, text="Tip: double-click a task to toggle done.").pack(side="right")

    def build_stats_tab(self):
        self.stats_label = ttk.Label(self.stats_tab, font=("Consolas", 14), justify="left")
        self.stats_label.pack(anchor="nw", padx=30, pady=30)

    def build_history_tab(self):
        frame = ttk.Frame(self.history_tab)
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.history_tree = ttk.Treeview(frame, columns=("time", "msg"), show="headings")
        self.history_tree.heading("time", text="Timestamp")
        self.history_tree.heading("msg", text="Activity")
        self.history_tree.column("time", width=170, anchor="w")
        self.history_tree.column("msg", width=700, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------- refresh ----------

    def refresh(self):
        # Task table
        self.tree.delete(*self.tree.get_children())

        keyword = self.search_var.get().strip().lower()
        flt = self.filter_var.get()

        for index, task in enumerate(self.tasks):
            status = get_status(task)

            if keyword and keyword not in task["name"].lower() and keyword not in task["client"].lower():
                continue
            if flt == "Pending" and status != "PENDING":
                continue
            if flt == "Completed" and status != "COMPLETED":
                continue
            if flt == "Overdue" and status != "OVERDUE":
                continue
            if flt == "High Priority" and task["priority"] != "High":
                continue

            # iid = real index in self.tasks, so filtering never breaks selection
            self.tree.insert(
                "", "end", iid=str(index), tags=(status,),
                values=(task["name"], task["client"], task["due_date"], task["priority"], status.title())
            )

        self.refresh_stats()
        self.refresh_history()

    def refresh_stats(self):
        total = len(self.tasks)
        statuses = [get_status(t) for t in self.tasks]
        completed = statuses.count("COMPLETED")
        pending = statuses.count("PENDING")
        overdue = statuses.count("OVERDUE")
        high = sum(1 for t in self.tasks if t["priority"] == "High")
        rate = (completed / total * 100) if total else 0

        self.stats_label.config(text=(
            f"Total tasks:      {total}\n"
            f"Completed:        {completed}\n"
            f"Pending:          {pending}\n"
            f"Overdue:          {overdue}\n"
            f"High priority:    {high}\n"
            f"Completion rate:  {rate:.1f}%"
        ))

    def refresh_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for item in reversed(self.history):
            self.history_tree.insert("", "end", values=(item["timestamp"], item["message"]))

    # ---------- actions ----------

    def selected_indexes(self):
        return sorted(int(iid) for iid in self.tree.selection())

    def add_task(self):
        name = self.name_var.get().strip()
        client = self.client_var.get().strip()
        due = self.due_var.get().strip()

        if not name:
            messagebox.showerror("Missing info", "Task name cannot be empty.")
            return
        if not client:
            messagebox.showerror("Missing info", "Client name cannot be empty.")
            return
        try:
            datetime.strptime(due, DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid date", "Please use the format YYYY-MM-DD.")
            return

        self.tasks.append({
            "name": name,
            "client": client,
            "due_date": due,
            "priority": self.priority_var.get(),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self.add_history(f"Created task '{name}' for client '{client}'.")
        self.save_data()

        self.name_var.set("")
        self.client_var.set("")
        self.refresh()

    def require_selection(self):
        indexes = self.selected_indexes()
        if not indexes:
            messagebox.showinfo("No selection", "Select one or more tasks first.")
        return indexes

    def complete_selected(self):
        for i in self.require_selection():
            task = self.tasks[i]
            if not task["completed"]:
                task["completed"] = True
                self.add_history(f"Completed task '{task['name']}'.")
        self.save_data()
        self.refresh()

    def undo_selected(self):
        for i in self.require_selection():
            task = self.tasks[i]
            if task["completed"]:
                task["completed"] = False
                self.add_history(f"Marked task '{task['name']}' as pending.")
        self.save_data()
        self.refresh()

    def toggle_selected(self):
        for i in self.selected_indexes():
            task = self.tasks[i]
            task["completed"] = not task["completed"]
            state = "Completed" if task["completed"] else "Marked as pending"
            self.add_history(f"{state} task '{task['name']}'.")
        self.save_data()
        self.refresh()

    def delete_selected(self):
        indexes = self.require_selection()
        if not indexes:
            return

        names = "\n".join(f"- {self.tasks[i]['name']}" for i in indexes)
        if not messagebox.askyesno("Confirm delete", f"Delete these tasks?\n\n{names}"):
            return

        for i in sorted(indexes, reverse=True):
            deleted = self.tasks.pop(i)
            self.add_history(f"Deleted task '{deleted['name']}'.")
        self.save_data()
        self.refresh()


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
