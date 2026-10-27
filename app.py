"""Tkinter interface for the modular educational simulator."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from . import APP_NAME, DISCLAIMER
from . import assistant, engine
from .catalog import SAMPLE_PROFILES, SYMPTOM_GROUPS, VITALS
from .reports import export_history_csv, format_report
from .storage import Database


COLORS = {
    "background": "#111923", "panel": "#1a2634", "panel2": "#223142",
    "text": "#e8eef5", "muted": "#aab7c5", "accent": "#46c3a8",
    "danger": "#ef7373", "warning": "#e6b85c", "border": "#314355",
}


class SimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1160x820")
        self.minsize(980, 700)
        self.configure(bg=COLORS["background"])
        self.db = Database()
        self.user = None
        self.latest_session = None
        self._configure_style()
        self.show_login()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=COLORS["background"])
        style.configure("Card.TFrame", background=COLORS["panel"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 21), foreground=COLORS["text"])
        style.configure("Heading.TLabel", font=("Segoe UI Semibold", 12))
        style.configure("TButton", padding=(11, 8), background=COLORS["panel2"], foreground=COLORS["text"])
        style.map("TButton", background=[("active", "#34495d")])
        style.configure("Accent.TButton", background="#18564e", foreground="#d4fff3", font=("Segoe UI Semibold", 10))
        style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["text"])
        style.map("TCheckbutton", background=[("active", COLORS["panel"])])
        style.configure("TEntry", fieldbackground="#101923", foreground=COLORS["text"], insertcolor=COLORS["text"], padding=7)
        style.configure("TCombobox", fieldbackground="#101923", foreground=COLORS["text"], padding=6)
        style.configure("Treeview", background=COLORS["panel"], fieldbackground=COLORS["panel"], foreground=COLORS["text"], rowheight=27)
        style.configure("Treeview.Heading", background=COLORS["panel2"], foreground=COLORS["text"], padding=6)
        style.map("Treeview", background=[("selected", "#18564e")])
        style.configure("TNotebook", background=COLORS["background"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["panel2"], foreground=COLORS["muted"], padding=(14, 9))
        style.map("TNotebook.Tab", background=[("selected", COLORS["panel"])], foreground=[("selected", COLORS["text"])])

    def show_login(self):
        for child in self.winfo_children():
            child.destroy()
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)
        card = tk.Frame(outer, bg=COLORS["panel"], padx=34, pady=28,
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.47, anchor="center", width=455)
        tk.Label(card, text="MEDICAL SIMULATOR", bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Segoe UI Semibold", 10)).pack(anchor="w")
        tk.Label(card, text="Welcome", bg=COLORS["panel"], fg=COLORS["text"],
                 font=("Segoe UI Semibold", 23)).pack(anchor="w", pady=(5, 4))
        tk.Label(card, text="Sign in, or create an account to save your simulation history.",
                 bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9),
                 wraplength=360, justify="left").pack(anchor="w", pady=(0, 17))

        self.login_username = tk.StringVar()
        self.login_display = tk.StringVar()
        self.login_password = tk.StringVar()
        self._form_field(card, "Username", self.login_username)
        self._form_field(card, "Display name (for new accounts)", self.login_display)
        self._form_field(card, "Password", self.login_password, show="*")
        self.login_message = tk.StringVar(value="")
        tk.Label(card, textvariable=self.login_message, bg=COLORS["panel"], fg=COLORS["danger"],
                 font=("Segoe UI", 9), wraplength=365, justify="left").pack(anchor="w", pady=(0, 8))
        actions = ttk.Frame(card)
        actions.pack(fill="x")
        ttk.Button(actions, text="Sign in", command=self._login).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(actions, text="Create account", style="Accent.TButton", command=self._create_account).pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(card, text=DISCLAIMER, bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 8),
                 wraplength=370, justify="left").pack(anchor="w", pady=(17, 0))

    def _form_field(self, parent, title, variable, show=None):
        tk.Label(parent, text=title, bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        entry = ttk.Entry(parent, textvariable=variable, show=show)
        entry.pack(fill="x", pady=(0, 11))
        return entry

    def _login(self):
        try:
            self.user = self.db.authenticate(self.login_username.get(), self.login_password.get())
            self.show_workspace()
        except ValueError as error:
            self.login_message.set(str(error))
        except Exception as error:
            self.login_message.set("Could not open the local database: " + str(error))

    def _create_account(self):
        try:
            self.user = self.db.register(self.login_username.get(), self.login_display.get(), self.login_password.get())
            self.show_workspace()
        except ValueError as error:
            self.login_message.set(str(error))
        except Exception as error:
            self.login_message.set("Could not create the account: " + str(error))

    def show_workspace(self):
        for child in self.winfo_children():
            child.destroy()
        header = tk.Frame(self, bg="#172432", height=47)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=APP_NAME, bg="#172432", fg=COLORS["text"],
                 font=("Segoe UI Semibold", 12)).pack(side="left", padx=16)
        tk.Label(header, text=DISCLAIMER, bg="#172432", fg=COLORS["muted"],
                 font=("Segoe UI", 8)).pack(side="left", padx=18)
        ttk.Button(header, text="Sign out", command=self._logout).pack(side="right", padx=12, pady=6)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)
        self.assessment_tab = AssessmentTab(self.notebook, self)
        self.history_tab = HistoryTab(self.notebook, self)
        self.assistant_tab = AssistantTab(self.notebook, self)
        self.profile_tab = ProfileTab(self.notebook, self)
        self.notebook.add(self.assessment_tab, text="Assessment")
        self.notebook.add(self.history_tab, text="History and trends")
        self.notebook.add(self.assistant_tab, text="Health assistant")
        self.notebook.add(self.profile_tab, text="Profile")
        self.title(APP_NAME + " - " + self.user["display_name"])

    def _logout(self):
        self.user = None
        self.latest_session = None
        self.title(APP_NAME)
        self.show_login()

    def run_assessment(self, source):
        try:
            symptoms, severity, duration, vitals = source.collect_inputs()
            if not symptoms and not vitals:
                raise ValueError("Select a symptom or enter at least one vital value.")
            assessment = engine.assess(symptoms, severity, duration, vitals)
            session = self.db.save_session(self.user["id"], symptoms, severity, duration, vitals, assessment)
            self.latest_session = session
            source.show_result(session)
            self.history_tab.refresh()
        except ValueError as error:
            messagebox.showerror("Check your entries", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Could not run simulation", str(error), parent=self)

    def export_current_report(self):
        if not self.latest_session:
            messagebox.showinfo("No result", "Run an assessment first.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self, title="Save text report", defaultextension=".txt",
            initialfile="medical_simulation_report.txt",
            filetypes=[("Text file", "*.txt")],
        )
        if not path:
            return
        try:
            Path(path).write_text(format_report(self.latest_session, self.user["display_name"]), encoding="utf-8")
            messagebox.showinfo("Report saved", "The text report was saved.", parent=self)
        except OSError as error:
            messagebox.showerror("Could not save report", str(error), parent=self)


class AssessmentTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app
        ttk.Label(self, text="New health simulation", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Choose symptoms and optionally enter values to explore the teaching rules.", style="Muted.TLabel").pack(anchor="w", pady=(3, 12))

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        left = tk.LabelFrame(content, text="Symptoms", bg=COLORS["panel"], fg=COLORS["text"],
                             padx=12, pady=9, font=("Segoe UI Semibold", 10))
        left.pack(side="left", fill="both", expand=True, padx=(0, 7))
        self.symptom_vars = {}
        for group, symptoms in SYMPTOM_GROUPS.items():
            tk.Label(left, text=group, bg=COLORS["panel"], fg=COLORS["accent"],
                     font=("Segoe UI Semibold", 9)).pack(anchor="w", pady=(7, 2))
            row = ttk.Frame(left)
            row.pack(fill="x", anchor="w")
            for index, symptom in enumerate(symptoms):
                variable = tk.BooleanVar(value=False)
                self.symptom_vars[symptom] = variable
                ttk.Checkbutton(row, text=symptom.title(), variable=variable).grid(
                    row=index // 2, column=index % 2, sticky="w", padx=(0, 10), pady=2)

        right = tk.LabelFrame(content, text="Details and vital values", bg=COLORS["panel"], fg=COLORS["text"],
                              padx=12, pady=9, font=("Segoe UI Semibold", 10), width=340)
        right.pack(side="left", fill="y", padx=(7, 0))
        right.pack_propagate(False)
        tk.Label(right, text="Symptom severity (1-10)", bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        self.severity = tk.DoubleVar(value=4)
        ttk.Scale(right, from_=1, to=10, variable=self.severity, orient="horizontal").pack(fill="x", pady=(5, 10))
        tk.Label(right, text="Duration in days", bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        self.duration = tk.StringVar(value="1")
        ttk.Spinbox(right, from_=1, to=365, textvariable=self.duration).pack(fill="x", pady=(4, 10))
        tk.Label(right, text="Sample values (optional)", bg=COLORS["panel"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        self.sample_name = tk.StringVar(value="Choose a sample")
        ttk.Combobox(right, textvariable=self.sample_name, values=list(SAMPLE_PROFILES), state="readonly").pack(fill="x", pady=(4, 4))
        ttk.Button(right, text="Apply sample values", command=self._apply_sample).pack(anchor="w", pady=(0, 9))
        self.vital_vars = {}
        for key, reference in VITALS.items():
            line = ttk.Frame(right)
            line.pack(fill="x", pady=3)
            tk.Label(line, text=reference["label"] + " (" + reference["unit"] + ")", bg=COLORS["panel"],
                     fg=COLORS["muted"], font=("Segoe UI", 8)).pack(side="left")
            variable = tk.StringVar(value="")
            self.vital_vars[key] = variable
            ttk.Entry(line, textvariable=variable, width=9).pack(side="right")

        footer = ttk.Frame(self)
        footer.pack(fill="x", pady=(12, 5))
        self.questions_button = ttk.Button(footer, text="Suggest follow-up questions", command=self._show_questions)
        self.questions_button.pack(side="left")
        ttk.Button(footer, text="Run simulation", style="Accent.TButton",
                   command=lambda: app.run_assessment(self)).pack(side="right")
        self.questions = tk.StringVar(value="")
        tk.Label(self, textvariable=self.questions, bg=COLORS["background"], fg=COLORS["muted"],
                 font=("Segoe UI", 9), justify="left", wraplength=950).pack(anchor="w", pady=(0, 6))

        self.result = tk.Text(self, height=11, wrap="word", bg=COLORS["panel"], fg=COLORS["text"],
                              insertbackground=COLORS["text"], relief="flat", padx=12, pady=10,
                              font=("Segoe UI", 9))
        self.result.pack(fill="both", expand=True, pady=(3, 0))
        self.result.insert("end", "Your latest simulation result will appear here.\n\n" + DISCLAIMER)
        self.result.configure(state="disabled")
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", pady=(7, 0))
        ttk.Button(buttons, text="Export latest result as text", command=app.export_current_report).pack(side="right")

    def _selected_symptoms(self):
        return [name for name, variable in self.symptom_vars.items() if variable.get()]

    def _show_questions(self):
        questions = engine.follow_up_questions(self._selected_symptoms())
        if not questions:
            self.questions.set("Select one or more symptoms first.")
        else:
            self.questions.set("Follow-up ideas: " + "  |  ".join(questions))

    def _apply_sample(self):
        profile = SAMPLE_PROFILES.get(self.sample_name.get())
        if profile:
            for key, value in profile.items():
                self.vital_vars[key].set(str(value))

    def collect_inputs(self):
        symptoms = self._selected_symptoms()
        try:
            severity = int(round(self.severity.get()))
            duration = int(self.duration.get())
        except (ValueError, tk.TclError) as error:
            raise ValueError("Enter a valid severity and duration.") from error
        if not 1 <= severity <= 10 or not 1 <= duration <= 365:
            raise ValueError("Severity must be 1-10 and duration must be 1-365 days.")
        vitals = {}
        for key, variable in self.vital_vars.items():
            value_text = variable.get().strip()
            if not value_text:
                continue
            try:
                value = float(value_text)
            except ValueError as error:
                raise ValueError("Enter a number for " + VITALS[key]["label"] + ".") from error
            if not VITALS[key]["min"] <= value <= VITALS[key]["max"]:
                raise ValueError(VITALS[key]["label"] + " is outside the allowed entry range.")
            vitals[key] = value
        return symptoms, severity, duration, vitals

    def show_result(self, session):
        assessment = session["assessment"]
        lines = [
            "SIMULATION RESULT",
            "Created: " + session["created_at"],
            "Symptoms: " + (", ".join(session["symptoms"]) or "None selected"),
            "",
            "Closest example patterns (match score, not disease probability):",
        ]
        if assessment["patterns"]:
            for pattern in assessment["patterns"]:
                lines.append("  " + pattern["name"] + " - " + str(round(pattern["score"] * 100)) + "%")
        else:
            lines.append("  No matching example pattern")
        lines.extend(["", "Teaching risk index: " + assessment["risk_level"] + " - " + str(assessment["risk_score"]) + "/10"])
        if assessment["abnormal_vitals"]:
            lines.append("Vital values outside the displayed ranges:")
            for item in assessment["abnormal_vitals"]:
                lines.append("  " + item["label"] + ": " + str(item["value"]) + " " + item["unit"] + " - " + item["status"])
        else:
            lines.append("No entered vital value was outside its displayed range.")
        if assessment["emergency_alerts"]:
            lines.extend(["", "URGENT ALERT PATTERN:"])
            lines.extend("  " + alert for alert in assessment["emergency_alerts"])
            lines.append("If this may be an emergency, contact local emergency services now.")
        lines.extend(["", DISCLAIMER, "This tool cannot diagnose or rule out a condition."])
        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("end", "\n".join(lines))
        self.result.configure(state="disabled")


class HistoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app
        ttk.Label(self, text="Your saved simulations", style="Title.TLabel").pack(anchor="w")
        self.summary = ttk.Label(self, text="", style="Muted.TLabel")
        self.summary.pack(anchor="w", pady=(3, 10))
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 7))
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(toolbar, text="Export history CSV", command=self.export_csv).pack(side="left", padx=7)
        columns = ("date", "pattern", "risk", "symptoms")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for key, title, width in (("date", "Created", 180), ("pattern", "Top pattern", 260), ("risk", "Risk index", 140), ("symptoms", "Symptoms", 440)):
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="w")
        self.table.pack(fill="x", expand=False)
        self.table.bind("<<TreeviewSelect>>", self._show_selected)
        ttk.Label(self, text="Vital value trends (latest 12 saved sessions)", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        self.chart = tk.Canvas(self, height=190, bg=COLORS["panel"], highlightthickness=0)
        self.chart.pack(fill="x")
        self.details = tk.StringVar(value="Select a saved row to see its details.")
        tk.Label(self, textvariable=self.details, bg=COLORS["background"], fg=COLORS["muted"],
                 font=("Segoe UI", 9), anchor="w", justify="left", wraplength=950).pack(fill="x", pady=(8, 0))
        self.records = {}
        self.refresh()

    def refresh(self):
        sessions = self.app.db.get_sessions(self.app.user["id"])
        self.records.clear()
        for item in self.table.get_children():
            self.table.delete(item)
        for session in sessions:
            assessment = session["assessment"]
            patterns = assessment.get("patterns", [])
            self.records[str(session["id"])] = session
            self.table.insert("", "end", iid=str(session["id"]), values=(
                session["created_at"].replace("T", " "),
                patterns[0]["name"] if patterns else "No pattern",
                assessment["risk_level"] + " - " + str(assessment["risk_score"]) + "/10",
                ", ".join(session["symptoms"]) or "No symptoms",
            ))
        self.summary.configure(text=f"Saved simulations: {len(sessions)}  |  Stored in the local SQLite database")
        self._draw_trends(list(reversed(sessions[:12])))

    def _show_selected(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return
        session = self.records[selected[0]]
        assessment = session["assessment"]
        self.details.set(
            "Symptoms: " + (", ".join(session["symptoms"]) or "none") +
            "   |   Risk: " + assessment["risk_level"] + " (" + str(assessment["risk_score"]) + "/10)" +
            "   |   Vitals entered: " + str(len(session["vitals"])) +
            "   |   Alerts: " + ("; ".join(assessment["emergency_alerts"]) or "none")
        )

    def _draw_trends(self, sessions):
        self.chart.delete("all")
        width = max(500, self.chart.winfo_width())
        self.chart.configure(width=width)
        left, top, plot_width = 60, 24, width - 95
        self.chart.create_text(left, 10, text="Temperature (C)", anchor="w", fill=COLORS["accent"], font=("Segoe UI", 8, "bold"))
        self.chart.create_text(left + 150, 10, text="Heart rate (bpm)", anchor="w", fill="#86a8e8", font=("Segoe UI", 8, "bold"))
        self.chart.create_line(left, top + 125, left + plot_width, top + 125, fill=COLORS["border"])
        if not sessions:
            self.chart.create_text(left + 10, top + 45, anchor="w", text="Save a simulation with vital values to see a trend.", fill=COLORS["muted"])
            return
        for key, label, color, low, high in (
            ("temperature_c", "Temp", COLORS["accent"], 35, 41),
            ("heart_rate_bpm", "Pulse", "#86a8e8", 40, 160),
        ):
            points = []
            for index, session in enumerate(sessions):
                value = session["vitals"].get(key)
                if value is None:
                    continue
                x = left + 10 + index * (plot_width - 20) / max(1, len(sessions) - 1)
                y = top + 112 - (max(low, min(high, value)) - low) * 85 / (high - low)
                points.extend([x, y])
                self.chart.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)
                self.chart.create_text(x, top + 142, text=str(index + 1), fill=COLORS["muted"], font=("Segoe UI", 7))
            if len(points) >= 4:
                self.chart.create_line(*points, fill=color, width=2, smooth=True)

    def export_csv(self):
        sessions = self.app.db.get_sessions(self.app.user["id"])
        if not sessions:
            messagebox.showinfo("No history", "There are no saved simulations to export.", parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Export history", defaultextension=".csv",
                                            filetypes=[("CSV file", "*.csv")], initialfile="simulation_history.csv")
        if path:
            try:
                export_history_csv(sessions, path)
                messagebox.showinfo("Export complete", "History was saved as a CSV file.", parent=self)
            except OSError as error:
                messagebox.showerror("Could not export", str(error), parent=self)


class AssistantTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app
        ttk.Label(self, text="Health education assistant", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="A small offline keyword helper. It cannot assess personal symptoms.", style="Muted.TLabel").pack(anchor="w", pady=(3, 12))
        self.chat = tk.Text(self, height=19, wrap="word", bg=COLORS["panel"], fg=COLORS["text"],
                            insertbackground=COLORS["text"], relief="flat", padx=12, pady=10)
        self.chat.pack(fill="both", expand=True)
        self.chat.insert("end", "Assistant: Ask about common terms or how this simulator works.\n")
        self.chat.configure(state="disabled")
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(9, 0))
        self.question = tk.StringVar()
        ttk.Entry(row, textvariable=self.question).pack(side="left", fill="x", expand=True, padx=(0, 7))
        ttk.Button(row, text="Ask", style="Accent.TButton", command=self._ask).pack(side="left")
        ttk.Button(self, text="Suggest questions about latest assessment", command=self._suggest).pack(anchor="w", pady=(9, 0))

    def _append(self, message):
        self.chat.configure(state="normal")
        self.chat.insert("end", message + "\n\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _ask(self):
        question = self.question.get().strip()
        if question:
            self._append("You: " + question + "\nAssistant: " + assistant.answer(question))
            self.question.set("")

    def _suggest(self):
        session = self.app.latest_session
        if not session:
            self._append("Assistant: Run an assessment first, then I can suggest follow-up prompts.")
            return
        questions = engine.follow_up_questions(session["symptoms"])
        self._append("Follow-up ideas:\n" + ("\n".join("- " + item for item in questions) if questions else "No symptoms were selected."))


class ProfileTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app
        ttk.Label(self, text="Local profile", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Optional information stays in the local SQLite database.", style="Muted.TLabel").pack(anchor="w", pady=(3, 12))
        panel = tk.Frame(self, bg=COLORS["panel"], padx=16, pady=15)
        panel.pack(fill="x", anchor="n")
        profile = app.db.get_profile(app.user["id"])
        self.age = tk.StringVar(value=str(profile["age"] if profile["age"] is not None else ""))
        tk.Label(panel, text="Age (optional)", bg=COLORS["panel"], fg=COLORS["muted"]).pack(anchor="w")
        ttk.Entry(panel, textvariable=self.age, width=16).pack(anchor="w", pady=(4, 12))
        tk.Label(panel, text="Notes (optional)", bg=COLORS["panel"], fg=COLORS["muted"]).pack(anchor="w")
        self.notes = tk.Text(panel, height=5, wrap="word", bg="#101923", fg=COLORS["text"], insertbackground=COLORS["text"], relief="flat")
        self.notes.pack(fill="x", pady=(4, 12))
        self.notes.insert("1.0", profile["notes"])
        ttk.Button(panel, text="Save profile", command=self._save).pack(anchor="w")
        ttk.Label(self, text="The app is a local learning tool. Do not store sensitive medical information here.", style="Muted.TLabel").pack(anchor="w", pady=(12, 0))

    def _save(self):
        raw_age = self.age.get().strip()
        try:
            age = int(raw_age) if raw_age else None
            if age is not None and not 0 <= age <= 125:
                raise ValueError
            self.app.db.save_profile(self.app.user["id"], age, self.notes.get("1.0", "end").strip())
            messagebox.showinfo("Saved", "Profile saved locally.", parent=self)
        except ValueError:
            messagebox.showerror("Check age", "Enter an age from 0 to 125, or leave it blank.", parent=self)
        except Exception as error:
            messagebox.showerror("Could not save", str(error), parent=self)


def launch():
    app = SimulatorApp()
    app.mainloop()

