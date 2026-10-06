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
                "Use the date format YYYY-MM-DD.",
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
