import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date, timedelta

try:
    import customtkinter as ctk
except ImportError:
    raise SystemExit(
        "CustomTkinter is not installed.\n"
        "Install it with: pip install customtkinter openpyxl"
    )

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    raise SystemExit(
        "openpyxl is not installed.\n"
        "Install it with: pip install openpyxl"
    )


# ============================================================
# TASK MANAGER - CUSTOMTKINTER EDITION
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "tasks.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "taskflow_settings.json")
DATE_FORMAT = "%m-%d-%Y"
TIME_FORMAT = "%H:%M"


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"appearance": "Dark"}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        appearance = data.get("appearance", "Dark")
        return {"appearance": appearance if appearance in {"Dark", "Light"} else "Dark"}
    except (json.JSONDecodeError, OSError):
        return {"appearance": "Dark"}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except OSError:
        pass


# ============================================================
# DATA
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return [], []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        tasks = data.get("tasks", [])
        history = data.get("history", [])

        # Add newer fields to older task records safely.
        for task in tasks:
            task.setdefault("description", "")
            task.setdefault("reminder_time", "")
            task.setdefault("reminder_sent", False)

        return tasks, history

    except (json.JSONDecodeError, OSError):
        messagebox.showwarning(
            "Load Error",
            "Could not load saved data. A new task list will be used."
        )
        return [], []


def get_status(task):
    if task.get("completed", False):
        return "COMPLETED"

    try:
        due = datetime.strptime(task["due_date"], DATE_FORMAT).date()
    except (KeyError, ValueError):
        return "PENDING"

    return "OVERDUE" if due < date.today() else "PENDING"


# ============================================================
# APPLICATION
# ============================================================

class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TaskFlow — Desktop Task Manager")
        self.geometry("1180x760")
        self.minsize(980, 650)

        ctk.set_default_color_theme("blue")

        self.tasks, self.history = load_data()
        self.settings = load_settings()
        self.appearance_mode = self.settings.get("appearance", "Dark")
        ctk.set_appearance_mode(self.appearance_mode)
        self.set_palette()
        self.configure(fg_color=self.bg)

        self.build_ui()
        self.refresh()

        # Check reminders periodically.
        self.after(30000, self.check_reminders)

    # --------------------------------------------------------
    # DATA HELPERS
    # --------------------------------------------------------

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"tasks": self.tasks, "history": self.history},
                    f,
                    indent=4,
                )
        except OSError as exc:
            messagebox.showerror("Save Error", f"Could not save data.\n\n{exc}")

    def add_history(self, message):
        self.history.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": message,
            }
        )

    # --------------------------------------------------------
    # THEME
    # --------------------------------------------------------

    def set_palette(self):
        if self.appearance_mode == "Light":
            self.bg = "#F4F6FA"
            self.panel = "#FFFFFF"
            self.panel_2 = "#EEF1F6"
            self.row = "#F9FAFC"
            self.border = "#D7DDE7"
            self.text = "#172033"
            self.muted = "#667085"
            self.accent = "#3B82F6"
            self.accent_hover = "#2563EB"
            self.success = "#21B77A"
            self.success_hover = "#159A66"
            self.warning = "#D99A17"
            self.danger = "#EF4B59"
            self.danger_hover = "#D93B49"
            self.neutral_button = "#E2E7EF"
            self.neutral_hover = "#D4DAE4"
        else:
            self.bg = "#0F1117"
            self.panel = "#171A21"
            self.panel_2 = "#1E232D"
            self.row = "#202631"
            self.border = "#2A303C"
            self.text = "#F4F6FA"
            self.muted = "#9AA3B2"
            self.accent = "#4F8CFF"
            self.accent_hover = "#3E76DC"
            self.success = "#39C98A"
            self.success_hover = "#2EAC76"
            self.warning = "#F5B84B"
            self.danger = "#FF5C68"
            self.danger_hover = "#E64B57"
            self.neutral_button = "#303746"
            self.neutral_hover = "#3A4354"

    def change_appearance(self, mode):
        self.appearance_mode = mode
        self.settings["appearance"] = mode
        save_settings(self.settings)

        # Rebuild the visible UI so every panel, field and button uses the
        # selected palette immediately.
        for widget in self.winfo_children():
            widget.destroy()

        ctk.set_appearance_mode(mode)
        self.set_palette()
        self.configure(fg_color=self.bg)
        self.build_ui()
        self.refresh()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(
            self,
            fg_color=self.panel,
            corner_radius=0,
            height=82,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=28)

        ctk.CTkLabel(
            title_box,
            text="TaskFlow",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.text,
        ).pack(anchor="w", pady=(11, 0))

        ctk.CTkLabel(
            title_box,
            text="Simple task planning, reminders & productivity tracking",
            font=ctk.CTkFont(size=12),
            text_color=self.muted,
        ).pack(anchor="w")

        # Appearance selector
        appearance_box = ctk.CTkFrame(header, fg_color="transparent")
        appearance_box.pack(side="right", padx=(10, 20))

        ctk.CTkLabel(
            appearance_box,
            text="Appearance",
            text_color=self.muted,
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=(0, 8))

        self.appearance_menu = ctk.CTkComboBox(
            appearance_box,
            values=["Dark", "Light"],
            width=110,
            height=36,
            corner_radius=10,
            state="readonly",
            command=self.change_appearance,
        )
        self.appearance_menu.set(self.appearance_mode)
        self.appearance_menu.pack(side="left", padx=(0, 14))

        ctk.CTkButton(
            appearance_box,
            text="Export to Excel",
            command=self.export_excel,
            width=145,
            height=38,
            corner_radius=12,
            fg_color=self.accent,
            hover_color=self.accent_hover,
        ).pack(side="left")

        # Main navigation
        self.tabs = ctk.CTkTabview(
            self,
            corner_radius=14,
            fg_color=self.panel,
            segmented_button_fg_color=self.panel_2,
            segmented_button_selected_color=self.accent,
            segmented_button_selected_hover_color=self.accent_hover,
            segmented_button_unselected_color=self.panel_2,
            segmented_button_unselected_hover_color=self.neutral_hover,
        )
        self.tabs.pack(fill="both", expand=True, padx=18, pady=18)

        self.tabs.add("Tasks")
        self.tabs.add("Statistics")
        self.tabs.add("Activity History")

        self.build_tasks_tab()
        self.build_stats_tab()
        self.build_history_tab()

    def build_tasks_tab(self):
        tab = self.tabs.tab("Tasks")

        # ----------------------------------------------------
        # CLEAN, NON-OVERLAPPING TASK FORM
        # ----------------------------------------------------
        form = ctk.CTkFrame(
            tab,
            fg_color=self.panel_2,
            corner_radius=16,
        )
        form.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(
            form,
            text="Create New Task",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.text,
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(16, 8))

        self.name_var = tk.StringVar()
        self.client_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Medium")
        self.due_var = tk.StringVar(value=date.today().strftime(DATE_FORMAT))
        self.reminder_var = tk.StringVar(value="")
        self.description_var = tk.StringVar()

        # Column sizing keeps each field separated and prevents stacking.
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(1, weight=2)
        form.grid_columnconfigure(2, weight=1)
        form.grid_columnconfigure(3, weight=2)

        # Row 1: primary information
        self.add_form_field(
            form, "Task Name", self.name_var, row=1, column=0,
            width=330, placeholder="e.g. Prepare weekly report"
        )
        self.add_form_field(
            form, "Client / Project", self.client_var, row=1, column=1,
            width=230, placeholder="e.g. ACME Project"
        )

        ctk.CTkLabel(
            form, text="Priority", text_color=self.muted
        ).grid(row=1, column=2, sticky="w", padx=10, pady=(4, 3))

        self.priority_box = ctk.CTkComboBox(
            form,
            values=["Low", "Medium", "High"],
            variable=self.priority_var,
            width=145,
            height=38,
            corner_radius=10,
            state="readonly",
        )
        self.priority_box.grid(row=2, column=2, sticky="w", padx=10, pady=(0, 12))

        self.add_form_field(
            form, "Due Date (MM-DD-YYYY)", self.due_var, row=1, column=3,
            width=180, placeholder="2026-10-06"
        )

        # Row 2: reminder / description / add action
        ctk.CTkLabel(
            form, text="Reminder Time (HH:MM)", text_color=self.muted
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(4, 3))

        ctk.CTkEntry(
            form,
            textvariable=self.reminder_var,
            width=180,
            height=38,
            corner_radius=10,
            placeholder_text="Optional • 14:30",
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 14))

        ctk.CTkLabel(
            form, text="Description", text_color=self.muted
        ).grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=(4, 3))

        ctk.CTkEntry(
            form,
            textvariable=self.description_var,
            height=38,
            corner_radius=10,
            placeholder_text="Optional task details",
        ).grid(row=4, column=1, columnspan=2, sticky="ew", padx=10, pady=(0, 14))

        ctk.CTkButton(
            form,
            text="＋  Add Task",
            command=self.add_task,
            width=150,
            height=40,
            corner_radius=12,
            fg_color=self.success,
            hover_color=self.success_hover,
            text_color="#07150F" if self.appearance_mode == "Dark" else "#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=4, column=3, sticky="w", padx=10, pady=(0, 14))

        # ----------------------------------------------------
        # SEARCH / FILTER
        # ----------------------------------------------------
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(
            bar, text="Search", text_color=self.muted
        ).pack(side="left", padx=(5, 7))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())

        ctk.CTkEntry(
            bar,
            textvariable=self.search_var,
            width=300,
            height=38,
            corner_radius=10,
            placeholder_text="Search task, client or description...",
        ).pack(side="left")

        ctk.CTkLabel(
            bar, text="Filter", text_color=self.muted
        ).pack(side="left", padx=(22, 7))

        self.filter_var = tk.StringVar(value="All")
        ctk.CTkComboBox(
            bar,
            values=["All", "Pending", "Completed", "Overdue", "High Priority"],
            variable=self.filter_var,
            state="readonly",
            width=170,
            height=38,
            corner_radius=10,
            command=lambda _: self.refresh(),
        ).pack(side="left")

        # ----------------------------------------------------
        # TASK LIST
        # ----------------------------------------------------
        list_card = ctk.CTkFrame(
            tab,
            fg_color=self.panel_2,
            corner_radius=16,
        )
        list_card.pack(fill="both", expand=True, padx=12, pady=6)

        self.task_scroll = ctk.CTkScrollableFrame(
            list_card,
            fg_color="transparent",
            corner_radius=12,
        )
        self.task_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        self.task_rows = {}

        # ----------------------------------------------------
        # ACTIONS
        # ----------------------------------------------------
        actions = ctk.CTkFrame(tab, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(6, 12))

        self.action_button(
            actions, "✓  Complete", self.complete_selected, self.success, self.success_hover
        ).pack(side="left", padx=4)

        self.action_button(
            actions, "↩  Undo", self.undo_selected, self.neutral_button, self.neutral_hover
        ).pack(side="left", padx=4)

        self.action_button(
            actions, "✎  Edit", self.edit_selected, self.accent, self.accent_hover
        ).pack(side="left", padx=4)

        self.action_button(
            actions, "🗑  Delete", self.delete_selected, self.danger, self.danger_hover
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            actions,
            text="Tip: click a task row to select it. Double-click to edit.",
            text_color=self.muted,
        ).pack(side="right", padx=5)

    def add_form_field(self, parent, label, variable, row, column, width=None, placeholder=""):
        ctk.CTkLabel(
            parent, text=label, text_color=self.muted
        ).grid(row=row, column=column, sticky="w", padx=20 if column == 0 else 10, pady=(4, 3))

        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=width if width else 200,
            height=38,
            corner_radius=10,
            placeholder_text=placeholder,
        )
        entry.grid(row=row + 1, column=column, sticky="ew", padx=20 if column == 0 else 10, pady=(0, 12))
        return entry

    def action_button(self, parent, text, command, color, hover):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=125,
            height=38,
            corner_radius=12,
            fg_color=color,
            hover_color=hover,
        )

    def build_stats_tab(self):
        tab = self.tabs.tab("Statistics")

        self.stats_grid = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )
        self.stats_grid.pack(fill="both", expand=True, padx=20, pady=20)

        self.stat_cards = {}
        labels = [
            ("total", "TOTAL TASKS"),
            ("completed", "COMPLETED"),
            ("pending", "PENDING"),
            ("overdue", "OVERDUE"),
            ("high", "HIGH PRIORITY"),
            ("rate", "COMPLETION RATE"),
        ]

        for i, (key, title) in enumerate(labels):
            card = ctk.CTkFrame(
                self.stats_grid,
                fg_color=self.panel_2,
                corner_radius=18,
                height=150,
            )
            card.grid(
                row=i // 3,
                column=i % 3,
                padx=10,
                pady=10,
                sticky="nsew",
            )
            self.stats_grid.grid_columnconfigure(i % 3, weight=1)
            self.stats_grid.grid_rowconfigure(i // 3, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                text_color=self.muted,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(pady=(28, 8))

            value = ctk.CTkLabel(
                card,
                text="0",
                text_color=self.text,
                font=ctk.CTkFont(size=30, weight="bold"),
            )
            value.pack()

            self.stat_cards[key] = value

    def build_history_tab(self):
        tab = self.tabs.tab("Activity History")

        self.history_scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.panel_2,
            corner_radius=16,
        )
        self.history_scroll.pack(fill="both", expand=True, padx=20, pady=20)

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    def refresh(self):
        self.refresh_task_list()
        self.refresh_stats()
        self.refresh_history()

    def refresh_task_list(self):
        for widget in self.task_scroll.winfo_children():
            widget.destroy()

        self.task_rows.clear()

        keyword = self.search_var.get().strip().lower()
        flt = self.filter_var.get()

        visible_count = 0

        for index, task in enumerate(self.tasks):
            status = get_status(task)
            name = task.get("name", "")
            client = task.get("client", "")
            priority = task.get("priority", "Medium")

            searchable = f"{name} {client} {task.get('description', '')}".lower()

            if keyword and keyword not in searchable:
                continue
            if flt == "Pending" and status != "PENDING":
                continue
            if flt == "Completed" and status != "COMPLETED":
                continue
            if flt == "Overdue" and status != "OVERDUE":
                continue
            if flt == "High Priority" and priority != "High":
                continue

            self.create_task_row(index, task, status)
            visible_count += 1

        if visible_count == 0:
            ctk.CTkLabel(
                self.task_scroll,
                text="No tasks found.",
                text_color=self.muted,
                font=ctk.CTkFont(size=15),
            ).pack(pady=50)

    def create_task_row(self, index, task, status):
        if status == "OVERDUE":
            accent = self.danger
        elif status == "COMPLETED":
            accent = self.success
        elif task.get("priority") == "High":
            accent = self.warning
        else:
            accent = self.accent

        row = ctk.CTkFrame(
            self.task_scroll,
            fg_color=self.row,
            corner_radius=14,
            border_width=1,
            border_color=self.border,
            height=76,
        )
        row.pack(fill="x", padx=4, pady=5)
        row.pack_propagate(False)

        indicator = ctk.CTkFrame(
            row,
            fg_color=accent,
            corner_radius=5,
            width=6,
        )
        indicator.pack(side="left", fill="y", padx=(0, 12))

        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=8)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        task_title = task.get("name", "Untitled")
        if status == "COMPLETED":
            task_title = "✓ " + task_title

        title_label = ctk.CTkLabel(
            top,
            text=task_title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.text,
            anchor="w",
        )
        title_label.pack(side="left")

        client_label = ctk.CTkLabel(
            top,
            text=f"  •  {task.get('client', '')}",
            text_color=self.muted,
            anchor="w",
        )
        client_label.pack(side="left")

        meta = ctk.CTkLabel(
            content,
            text=(
                f"Due: {task.get('due_date', '')}   "
                f"|   Priority: {task.get('priority', 'Medium')}   "
                f"|   {status.title()}"
            ),
            text_color=accent,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        )
        meta.pack(anchor="w", pady=(2, 0))

        if task.get("reminder_time"):
            reminder = ctk.CTkLabel(
                row,
                text=f"🔔 {task['reminder_time']}",
                text_color=self.muted,
                font=ctk.CTkFont(size=11),
            )
            reminder.pack(side="right", padx=12)

        edit = ctk.CTkButton(
            row,
            text="Edit",
            command=lambda i=index: self.edit_task(i),
            width=65,
            height=30,
            corner_radius=9,
            fg_color=self.neutral_button,
            hover_color=self.neutral_hover,
        )
        edit.pack(side="right", padx=5)

        # Clicking anywhere in the row selects it.
        widgets = [row, indicator, content, top, title_label, client_label, meta]
        for widget in widgets:
            widget.bind("<Button-1>", lambda _e, i=index: self.select_row(i))
            widget.bind("<Double-Button-1>", lambda _e, i=index: self.edit_task(i))

        self.task_rows[index] = row

    def select_row(self, index):
        for i, row in self.task_rows.items():
            row.configure(
                border_color=self.accent if i == index else self.border,
                border_width=2 if i == index else 1,
            )
        self.selected_index = index

    # --------------------------------------------------------
    # STATS / HISTORY
    # --------------------------------------------------------

    def refresh_stats(self):
        total = len(self.tasks)
        statuses = [get_status(t) for t in self.tasks]
        completed = statuses.count("COMPLETED")
        pending = statuses.count("PENDING")
        overdue = statuses.count("OVERDUE")
        high = sum(1 for t in self.tasks if t.get("priority") == "High")
        rate = (completed / total * 100) if total else 0

        values = {
            "total": str(total),
            "completed": str(completed),
            "pending": str(pending),
            "overdue": str(overdue),
            "high": str(high),
            "rate": f"{rate:.1f}%",
        }

        for key, value in values.items():
            self.stat_cards[key].configure(text=value)

    def refresh_history(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        if not self.history:
            ctk.CTkLabel(
                self.history_scroll,
                text="No activity yet.",
                text_color=self.muted,
            ).pack(pady=40)
            return

        for item in reversed(self.history):
            card = ctk.CTkFrame(
                self.history_scroll,
                fg_color=self.row,
                corner_radius=12,
            )
            card.pack(fill="x", padx=5, pady=4)

            ctk.CTkLabel(
                card,
                text=item.get("timestamp", ""),
                text_color=self.muted,
                width=155,
                anchor="w",
            ).pack(side="left", padx=15, pady=12)

            ctk.CTkLabel(
                card,
                text=item.get("message", ""),
                text_color=self.text,
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=8, pady=12)

    # --------------------------------------------------------
    # TASK ACTIONS
    # --------------------------------------------------------

    def require_selection(self):
        if not hasattr(self, "selected_index") or self.selected_index not in range(len(self.tasks)):
            messagebox.showinfo("No Selection", "Select a task first.")
            return None
        return self.selected_index

    def add_task(self):
        name = self.name_var.get().strip()
        client = self.client_var.get().strip()
        due = self.due_var.get().strip()
        reminder = self.reminder_var.get().strip()
        description = self.description_var.get().strip()

        if not name:
            messagebox.showerror("Missing Info", "Task name cannot be empty.")
            return

        if not client:
            messagebox.showerror("Missing Info", "Client / Project cannot be empty.")
            return

        if not self.valid_date(due):
            return

        if reminder and not self.valid_time(reminder):
            return

        self.tasks.append(
            {
                "name": name,
                "client": client,
                "due_date": due,
                "priority": self.priority_var.get(),
                "description": description,
                "reminder_time": reminder,
                "reminder_sent": False,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        self.add_history(f"Created task '{name}' for '{client}'.")
        self.save_data()

        self.name_var.set("")
        self.client_var.set("")
        self.priority_var.set("Medium")
        self.due_var.set(date.today().strftime(DATE_FORMAT))
        self.reminder_var.set("")
        self.description_var.set("")

        self.refresh()

    def complete_selected(self):
        index = self.require_selection()
        if index is None:
            return

        task = self.tasks[index]
        if not task.get("completed"):
            task["completed"] = True
            self.add_history(f"Completed task '{task['name']}'.")
            self.save_data()
            self.refresh()

    def undo_selected(self):
        index = self.require_selection()
        if index is None:
            return

        task = self.tasks[index]
        if task.get("completed"):
            task["completed"] = False
            task["reminder_sent"] = False
            self.add_history(f"Marked task '{task['name']}' as pending.")
            self.save_data()
            self.refresh()

    def edit_selected(self):
        index = self.require_selection()
        if index is not None:
            self.edit_task(index)

    def edit_task(self, index):
        task = self.tasks[index]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("520x570")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.bg)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Edit Task",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(24, 16))

        fields = {}

        def add_field(label, value, placeholder=""):
            ctk.CTkLabel(dialog, text=label, text_color=self.muted).pack(
                anchor="w", padx=35, pady=(8, 3)
            )
            entry = ctk.CTkEntry(
                dialog,
                width=450,
                height=38,
                corner_radius=10,
                placeholder_text=placeholder,
            )
            entry.insert(0, value)
            entry.pack(padx=35)
            fields[label] = entry

        add_field("Task Name", task.get("name", ""))
        add_field("Client / Project", task.get("client", ""))
        add_field("Due Date (MM-DD-YYYY)", task.get("due_date", ""))
        add_field("Reminder Time (HH:MM)", task.get("reminder_time", ""))
        add_field("Description", task.get("description", ""))

        ctk.CTkLabel(dialog, text="Priority", text_color=self.muted).pack(
            anchor="w", padx=35, pady=(8, 3)
        )
        priority = ctk.CTkComboBox(
            dialog,
            values=["Low", "Medium", "High"],
            width=450,
            height=38,
            corner_radius=10,
        )
        priority.set(task.get("priority", "Medium"))
        priority.pack(padx=35)

        def save_edit():
            name = fields["Task Name"].get().strip()
            client = fields["Client / Project"].get().strip()
            due = fields["Due Date (MM-DD-YYYY)"].get().strip()
            reminder = fields["Reminder Time (HH:MM)"].get().strip()

            if not name or not client:
                messagebox.showerror(
                    "Missing Info",
                    "Task name and Client / Project are required.",
                    parent=dialog,
                )
                return

            if not self.valid_date(due, parent=dialog):
                return

            if reminder and not self.valid_time(reminder, parent=dialog):
                return

            old_name = task.get("name", "")

            task["name"] = name
            task["client"] = client
            task["due_date"] = due
            task["reminder_time"] = reminder
            task["description"] = fields["Description"].get().strip()
            task["priority"] = priority.get()

            # New/changed reminder should be eligible for a notification.
            task["reminder_sent"] = False

            self.add_history(f"Edited task '{old_name}'.")
            self.save_data()
            dialog.destroy()
            self.refresh()

        button_row = ctk.CTkFrame(dialog, fg_color="transparent")
        button_row.pack(fill="x", padx=35, pady=25)

        ctk.CTkButton(
            button_row,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            height=38,
            corner_radius=11,
            fg_color=self.neutral_button,
        ).pack(side="left")

        ctk.CTkButton(
            button_row,
            text="Save Changes",
            command=save_edit,
            width=150,
            height=38,
            corner_radius=11,
            fg_color=self.accent,
            hover_color=self.accent_hover,
        ).pack(side="right")

    def delete_selected(self):
        index = self.require_selection()
        if index is None:
            return

        task = self.tasks[index]

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete this task?\n\n{task.get('name', '')}",
        ):
            return

        deleted = self.tasks.pop(index)
        self.add_history(f"Deleted task '{deleted['name']}'.")
        self.save_data()

        if hasattr(self, "selected_index"):
            del self.selected_index

        self.refresh()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    def valid_date(self, value, parent=None):
        try:
            datetime.strptime(value, DATE_FORMAT)
            return True
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Use the date format MM-DD-YYYY.",
                parent=parent,
            )
            return False

    def valid_time(self, value, parent=None):
        try:
            datetime.strptime(value, TIME_FORMAT)
            return True
        except ValueError:
            messagebox.showerror(
                "Invalid Time",
                "Use the time format HH:MM, for example 14:30.",
                parent=parent,
            )
            return False

    # --------------------------------------------------------
    # REMINDERS
    # --------------------------------------------------------

    def check_reminders(self):
        now = datetime.now()

        for task in self.tasks:
            if task.get("completed"):
                continue

            reminder_time = task.get("reminder_time", "").strip()
            due_date = task.get("due_date", "").strip()

            if not reminder_time or not due_date:
                continue

            try:
                reminder_dt = datetime.strptime(
                    f"{due_date} {reminder_time}",
                    "%Y-%m-%d %H:%M",
                )
            except ValueError:
                continue

            # Reminder is valid during the minute after its scheduled time.
            if (
                reminder_dt <= now < reminder_dt + timedelta(minutes=1)
                and not task.get("reminder_sent", False)
            ):
                task["reminder_sent"] = True
                self.add_history(f"Reminder triggered for '{task['name']}'.")
                self.save_data()

                self.bell()
                messagebox.showinfo(
                    "Task Reminder",
                    f"Reminder:\n\n{task['name']}\n\n"
                    f"Due: {task['due_date']}\n"
                    f"Priority: {task.get('priority', 'Medium')}",
                )

        self.after(30000, self.check_reminders)

    # --------------------------------------------------------
    # EXCEL EXPORT
    # --------------------------------------------------------

    def export_excel(self):
        if not self.tasks:
            messagebox.showinfo("Export", "There are no tasks to export.")
            return

        default_name = f"taskflow_export_{date.today().strftime('%Y%m%d')}.xlsx"

        path = filedialog.asksaveasfilename(
            title="Export Tasks to Excel",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel Workbook", "*.xlsx")],
        )

        if not path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Tasks"

            headers = [
                "Task",
                "Client / Project",
                "Due Date",
                "Priority",
                "Status",
                "Reminder Time",
                "Description",
                "Created At",
            ]

            ws.append(headers)

            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="4F8CFF")
                cell.alignment = Alignment(horizontal="center")

            for task in self.tasks:
                ws.append(
                    [
                        task.get("name", ""),
                        task.get("client", ""),
                        task.get("due_date", ""),
                        task.get("priority", ""),
                        get_status(task).title(),
                        task.get("reminder_time", ""),
                        task.get("description", ""),
                        task.get("created_at", ""),
                    ]
                )

            widths = [32, 24, 15, 12, 14, 16, 45, 22]
            for i, width in enumerate(widths, start=1):
                ws.column_dimensions[chr(64 + i)].width = width

            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

            # Add a summary sheet.
            summary = wb.create_sheet("Summary")
            summary["A1"] = "TaskFlow Summary"
            summary["A1"].font = Font(size=18, bold=True)
            summary["A3"] = "Total Tasks"
            summary["B3"] = len(self.tasks)
            summary["A4"] = "Completed"
            summary["B4"] = sum(get_status(t) == "COMPLETED" for t in self.tasks)
            summary["A5"] = "Pending"
            summary["B5"] = sum(get_status(t) == "PENDING" for t in self.tasks)
            summary["A6"] = "Overdue"
            summary["B6"] = sum(get_status(t) == "OVERDUE" for t in self.tasks)
            summary["A7"] = "High Priority"
            summary["B7"] = sum(
                t.get("priority") == "High" for t in self.tasks
            )

            wb.save(path)

            self.add_history(f"Exported tasks to Excel: {os.path.basename(path)}")
            self.save_data()
            self.refresh_history()

            messagebox.showinfo(
                "Export Complete",
                f"Excel file created successfully.\n\n{path}",
            )

        except Exception as exc:
            messagebox.showerror(
                "Export Error",
                f"Could not create the Excel file.\n\n{exc}",
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
