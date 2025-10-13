import os
import csv
import math
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
from difflib import get_close_matches

# GUI-related imports will be imported locally in functions that need them
# import tkinter as tk
# from tkinter import filedialog, messagebox
# import ttkbootstrap as ttk  # using ttkbootstrap for styling
# from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO, DANGER, SECONDARY

# ====================================================
# Helper Functions
# ====================================================

def format_time(time_in_minutes):
    """Converts a float (minutes) to a string 'M minutes S seconds'."""
    minutes = int(math.floor(time_in_minutes))
    seconds = int(round((time_in_minutes - minutes) * 60))
    return f"{minutes} minutes {seconds} seconds"

class AutocompleteCombobox(ttk.Combobox):
    """
    A combobox that provides autocomplete suggestions based on a provided list.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self.bind('<KeyRelease>', self._handle_keyrelease)

    def set_completion_list(self, completion_list):
        """Sort and store the list; also update the combobox values."""
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list

    def _handle_keyrelease(self, event):
        if event.keysym in ("BackSpace", "Left", "Right", "Delete", "Tab"):
            return
        value = self.get()
        data = self._completion_list if not value else [item for item in self._completion_list if item.lower().startswith(value.lower())]
        self['values'] = data

def get_column(df, candidates, col_description="column"):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    raise ValueError(f"CSV file must contain one of the following {col_description}: {', '.join(candidates)}")

def parse_datetime(dt_str):
    try:
        return datetime.strptime(dt_str.strip(), '%Y-%m-%d %H:%M:%S')
    except Exception:
        raise ValueError(f"Invalid datetime format: {dt_str}. Expected format: YYYY-MM-DD HH:MM:SS")

def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    return merged

def compute_total_duration(intervals):
    total = timedelta()
    for start, end in intervals:
        total += (end - start)
    return total.total_seconds() / 60

def intersect_interval(interval, period):
    start, end = interval
    p_start, p_end = period
    new_start = max(start, p_start)
    new_end = min(end, p_end)
    return (new_start, new_end) if new_start < new_end else None

def get_global_times(file_path):
    try:
        df = pd.read_csv(file_path, skiprows=3)
        df.columns = df.columns.str.strip()
    except Exception as e:
        raise ValueError(f"Error reading file '{file_path}' for global times: {e}")
    name_col = get_column(df, ["Name", "Name (Original Name)", "Name (original name)"], "name column")
    join_col = get_column(df, ["Join Time", "Join time"], "Join Time")
    leave_col = get_column(df, ["Leave Time", "Leave time"], "Leave Time")
    try:
        df[join_col] = pd.to_datetime(df[join_col])
        df[leave_col] = pd.to_datetime(df[leave_col])
    except Exception as e:
        raise ValueError(f"Error converting join/leave times in '{file_path}': {e}")
    df["Name_lower"] = df[name_col].str.lower()
    global_times = {}
    for name_lower, group in df.groupby("Name_lower"):
        global_times[name_lower] = (group[join_col].min(), group[leave_col].max())
    return global_times

def get_total_durations(file_path):
    try:
        df = pd.read_csv(file_path, skiprows=3)
        df.columns = df.columns.str.strip()
        name_col = get_column(df, ["Name", "Name (Original Name)", "Name (original name)"], "name column")
        duration_col = get_column(df, ["Duration", "Duration (minutes)"], "duration column")
        df[duration_col] = pd.to_numeric(df[duration_col], errors="coerce")
        df["Name_lower"] = df[name_col].str.lower()
        return df.groupby("Name_lower")[duration_col].sum().to_dict()
    except Exception as e:
        raise ValueError(f"Error computing total durations from '{file_path}': {e}")

def process_csv_session(file_path, session_start, session_end, time_required):
    try:
        df = pd.read_csv(file_path, skiprows=3)
        df.columns = df.columns.str.strip()
    except Exception as e:
        raise ValueError(f"Error reading file '{file_path}': {e}")
    name_col = get_column(df, ["Name", "Name (Original Name)", "Name (original name)"], "name column")
    email_col = get_column(df, ["Email", "User Email"], "Email")
    join_col = get_column(df, ["Join Time", "Join time"], "Join Time")
    leave_col = get_column(df, ["Leave Time", "Leave time"], "Leave Time")
    try:
        df[join_col] = pd.to_datetime(df[join_col])
        df[leave_col] = pd.to_datetime(df[leave_col])
    except Exception as e:
        raise ValueError(f"Error converting join/leave times in '{file_path}': {e}")
    df["Name_lower"] = df[name_col].str.lower()
    session_results = {}
    for name_lower, group in df.groupby("Name_lower"):
        original_name = group.iloc[0][name_col]
        email = group.iloc[0][email_col]
        intervals = [(row[join_col], row[leave_col]) for _, row in group.iterrows()]
        merged = merge_intervals(intervals)
        session_intervals = [intersect_interval(interval, (session_start, session_end))
                             for interval in merged if intersect_interval(interval, (session_start, session_end))]
        session_intervals = merge_intervals(session_intervals)
        session_duration = compute_total_duration(session_intervals)
        if session_duration >= time_required:
            status = "P"
            shortfall = 0
        else:
            status = "A"
            shortfall = round(time_required - session_duration, 2)
        session_results[name_lower] = {
            "Name": original_name,
            "Email": email,
            "session_duration": session_duration,
            "status": status,
            "shortfall": shortfall
        }
    return session_results

def process_sessions_for_file(file_path, sessions_info):
    global_participants = {}
    total_sessions = len(sessions_info)
    session_labels = []
    for session_index, session in enumerate(sessions_info, start=1):
        try:
            session_results = process_csv_session(file_path, session["session_start"], session["session_end"], session["time_required"])
            session_global_times = get_global_times(file_path)
        except ValueError as ve:
            raise ValueError(str(ve))
        for name_lower, details in session_results.items():
            if name_lower not in session_global_times:
                continue
            g_join, g_leave = session_global_times[name_lower]
            session_detail = {
                "status": details["status"],
                "shortfall": details["shortfall"],
                "session_duration": details["session_duration"]
            }
            if name_lower not in global_participants:
                global_participants[name_lower] = {
                    "Name": details["Name"],
                    "Email": details["Email"],
                    "global_join": g_join,
                    "global_leave": g_leave,
                    "total_duration": details["session_duration"],
                    "sessions": {session_index: session_detail}
                }
            else:
                curr = global_participants[name_lower]
                curr["global_join"] = min(curr["global_join"], g_join)
                curr["global_leave"] = max(curr["global_leave"], g_leave)
                curr["total_duration"] += details["session_duration"]
                curr["sessions"][session_index] = session_detail
        session_labels.append(f"Session {session_index} ({session['session_start'].strftime('%Y-%m-%d %H:%M:%S')})")
    for participant in global_participants.values():
        for i in range(1, total_sessions + 1):
            if i not in participant["sessions"]:
                req = sessions_info[i-1]["time_required"]
                participant["sessions"][i] = {"status": "A", "shortfall": req, "session_duration": 0}
    try:
        raw_durations = get_total_durations(file_path)
    except Exception as e:
        raise ValueError(str(e))
    for name_lower, participant in global_participants.items():
        if name_lower in raw_durations:
            participant["total_duration"] = raw_durations[name_lower]
    output_records = []
    for participant in global_participants.values():
        record = {
            "Name": participant["Name"],
            "Email": participant["Email"],
            "Join Time": participant["global_join"].strftime('%Y-%m-%d %H:%M:%S'),
            "Leave Time": participant["global_leave"].strftime('%Y-%m-%d %H:%M:%S')
        }
        for i in range(1, total_sessions + 1):
            record[session_labels[i-1]] = participant["sessions"][i]["status"]
        record["Total Duration"] = round(participant["total_duration"], 2)
        breakdown_msgs = []
        for i in range(1, total_sessions + 1):
            sess = participant["sessions"][i]
            if sess["status"] == "A":
                req = sessions_info[i-1]["time_required"]
                computed = sess["session_duration"]
                breakdown_msgs.append(f"User duration is just {format_time(computed)} out of {format_time(req)} minutes, which is why marking absent in {session_labels[i-1]}")
        record["Shortfall Reason"] = "; ".join(breakdown_msgs) if breakdown_msgs else ""
        output_records.append(record)
    session_summary = []
    for i in range(1, total_sessions + 1):
        present_count = sum(1 for p in global_participants.values() if p["sessions"].get(i, {}).get("status", "A") == "P")
        absent_count = sum(1 for p in global_participants.values() if p["sessions"].get(i, {}).get("status", "A") == "A")
        session_summary.append(f"Session {i}: Present: {present_count}, Absent: {absent_count}")
    return output_records, session_labels, session_summary

def write_excel(raw_log_df, output_records, output_file):
    try:
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            raw_log_df.to_excel(writer, sheet_name="Sheet1", index=False, header=False)
            pd.DataFrame(output_records).to_excel(writer, sheet_name="Attendance", index=False)
    except Exception as e:
        raise ValueError(f"Error saving output Excel file: {e}")

def match_names_v4(main_name, zoom_names):
    valid_zoom_names = [name for name in zoom_names if isinstance(name, str)]
    if main_name in valid_zoom_names:
        return main_name
    main_parts = main_name.lower().split()
    for zoom_name in valid_zoom_names:
        zoom_parts = zoom_name.lower().split()
        if len(main_parts) >= 2:
            if main_parts[0] in zoom_parts and main_parts[-1] in zoom_parts:
                return zoom_name
        if len(main_parts) == 1 and main_parts[0] in zoom_parts:
            return zoom_name
    return None

def process_file_match(input_path, output_path, silent=False):
    df = pd.read_excel(input_path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    main_list = df.iloc[:, 1]
    zoom_log_names = df.iloc[:, 2]
    arranged_data_v4 = df.iloc[:, :2].copy()
    for col in df.columns[2:]:
        arranged_data_v4[col] = 'N/A'
    unmatched_zoom_log_v4 = []
    for index, main_name in enumerate(main_list):
        if pd.isna(main_name):
            continue
        matched_name = match_names_v4(main_name, zoom_log_names)
        if matched_name:
            matched_row = df[df.iloc[:, 2] == matched_name].iloc[0]
            arranged_data_v4.iloc[index, 2:] = matched_row.iloc[2:]
    for zoom_name in zoom_log_names:
        if pd.isna(zoom_name) or zoom_name in arranged_data_v4.iloc[:, 2].values:
            continue
        unmatched_row = df[df.iloc[:, 2] == zoom_name].iloc[0]
        unmatched_zoom_log_v4.append(unmatched_row)
    unmatched_df = pd.DataFrame(unmatched_zoom_log_v4)
    with pd.ExcelWriter(output_path) as writer:
        arranged_data_v4.to_excel(writer, index=False, sheet_name="Matched Records")
        unmatched_df.to_excel(writer, index=False, sheet_name="Unmatched Records")
    if not silent:
        messagebox.showinfo("Success", f"Data arranged successfully! Saved to: {output_path}")

# ====================================================
# Attendance Generator Tool as a Class
# ====================================================

class AttendanceGeneratorApp:
    def __init__(self, master, back_callback):
        self.master = master
        self.back_callback = back_callback

        # Global style initialization
        self.style = ttk.Style()
        self.current_theme = "flatly"
        self.style.theme_use(self.current_theme)
        self.style.configure("Header.TLabel", foreground="#1a73e8", font=("Helvetica", 20, "bold"))

        # Header Section
        self.header_frame = ttk.Frame(master, padding=20)
        self.header_frame.pack(fill='x')
        self.title_label = ttk.Label(self.header_frame, text="Advanced Zoom Attendance Generator", style="Header.TLabel")
        self.title_label.pack()
        self.style.configure("SubHeader.TLabel", foreground="#1a73e8", font=("Helvetica", 12))
        self.subtitle_label = ttk.Label(self.header_frame,
                                        text="An AI-powered tool for automated Zoom attendance tracking.",
                                        style="SubHeader.TLabel")
        self.subtitle_label.pack()

        # Main Container
        self.main_frame = ttk.Frame(master, padding=15)
        self.main_frame.pack(fill='both', expand=True)

        # Mode Selection Area
        mode_frame = ttk.LabelFrame(self.main_frame, text="Select Mode", padding=10)
        mode_frame.pack(fill='x', pady=10)
        self.mode_mapping = {
            "Single CSV File with Multiple Sessions": "single",
            "Multiple CSV Files (Generate Excel per File)": "multiple"
        }
        self.mode_var = tk.StringVar(value="Single CSV File with Multiple Sessions")
        self.mode_combobox = ttk.Combobox(mode_frame,
                                          textvariable=self.mode_var,
                                          values=list(self.mode_mapping.keys()),
                                          state="readonly")
        self.mode_combobox.pack(side="left", padx=5)
        self.mode_combobox.bind("<<ComboboxSelected>>", lambda e: self.switch_mode())

        # CSV File Selection
        file_frame = ttk.LabelFrame(self.main_frame, text="CSV File Selection", padding=10)
        file_frame.pack(fill='x', pady=10)
        self.file_button = ttk.Button(file_frame, text="Select CSV File(s)", command=self.select_files, bootstyle=INFO)
        self.file_button.pack(side="left", padx=5)
        self.file_label = ttk.Entry(file_frame, width=50)
        self.file_label.pack(side="left", padx=5, fill="x", expand=True)
        self.file_label.configure(state="readonly")
        self.file_mapping = {}
        self.selected_file = None
        self.selected_files = []

        # Session Config CSV Selection
        session_config_frame = ttk.LabelFrame(self.main_frame, text="Session Config CSV Selection", padding=10)
        session_config_frame.pack(fill='x', pady=10)
        self.session_config_button = ttk.Button(session_config_frame, text="Load Session Config CSV",
                                                command=self.load_session_config, bootstyle=INFO)
        self.session_config_button.pack(side="left", padx=5)
        self.session_config_label = ttk.Entry(session_config_frame, width=50)
        self.session_config_label.pack(side="left", padx=5, fill="x", expand=True)
        self.session_config_label.configure(state="readonly")
        self.session_config_options = []
        self.session_config_mapping = {}

        # Session Details Table
        session_frame = ttk.LabelFrame(self.main_frame, text="Session Details", padding=10)
        session_frame.pack(fill='both', pady=10, expand=True)
        header_row = ttk.Frame(session_frame)
        header_row.pack(fill="x", pady=5)
        ttk.Label(header_row, text="File", width=20, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=3)
        ttk.Label(header_row, text="Session Config", width=30, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=3)
        ttk.Label(header_row, text="Session Start", width=20, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=3)
        ttk.Label(header_row, text="Session End", width=20, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=3, padx=3)
        ttk.Label(header_row, text="Time Required (min)", width=20, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=4, padx=3)
        ttk.Label(header_row, text="Remove", width=10, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=0, column=5, padx=3)
        self.sessions_container = ttk.Frame(session_frame)
        self.sessions_container.pack(fill="both", expand=True)
        self.session_rows = []

        # Action Buttons
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill='x', pady=10)
        self.add_session_button = ttk.Button(action_frame, text="Add Session", command=self.add_session, bootstyle=SUCCESS)
        self.add_session_button.pack(side="left", padx=5)
        self.generate_button = ttk.Button(action_frame, text="Generate Attendance", command=self.generate_attendance, bootstyle=PRIMARY)
        self.generate_button.pack(side="right", padx=5)

        # Progress Indicator
        self.progress_bar = ttk.Progressbar(self.main_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.pack_forget()

        # Bottom Navigation (Back button)
        bottom_nav = ttk.Frame(master, padding=10)
        bottom_nav.pack(fill='x', side='bottom')
        back_button = ttk.Button(bottom_nav, text="Back", command=self.go_back, bootstyle=SECONDARY)
        back_button.pack(side="left")
        self.theme_toggle = ttk.Button(bottom_nav, text="Toggle Dark/Light Theme", command=self.toggle_theme, bootstyle=SECONDARY)
        self.theme_toggle.pack(side="left", padx=5)
        self.footer_label = ttk.Label(bottom_nav, text="App v1.2 created by Satendra Goswami", font=('Helvetica', 8), foreground="gray")
        self.footer_label.pack(side="right")

        self.switch_mode()

    def go_back(self):
        # Simply call the back callback to clear and rebuild the main menu
        self.back_callback()

    def switch_mode(self):
        mode = self.mode_mapping[self.mode_var.get()]
        for widget in self.sessions_container.winfo_children():
            widget.destroy()
        self.session_rows.clear()
        self.file_label.configure(state="normal")
        self.file_label.delete(0, tk.END)
        self.file_label.configure(state="readonly")
        self.file_mapping.clear()
        self.selected_file = None
        self.selected_files = []
        self.file_button.config(text="Select CSV File" if mode == "single" else "Select CSV Files")

    def select_files(self):
        mode = self.mode_mapping[self.mode_var.get()]
        if mode == "single":
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")],
                                                   title="Select Zoom Log CSV File")
            if file_path:
                self.selected_file = file_path
                self.file_label.configure(state="normal")
                self.file_label.delete(0, tk.END)
                self.file_label.insert(0, os.path.basename(file_path))
                self.file_label.configure(state="readonly")
        else:
            files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")],
                                                title="Select Zoom Log CSV Files")
            if files:
                self.selected_files = list(files)
                self.file_mapping = {os.path.basename(f): f for f in self.selected_files}
                self.file_label.configure(state="normal")
                self.file_label.delete(0, tk.END)
                self.file_label.insert(0, f"{len(self.selected_files)} file(s) selected")
                self.file_label.configure(state="readonly")

    def load_session_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")],
                                               title="Select Session Config CSV File")
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            required_cols = ["Session Start", "Session End", "Time Required"]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Session Config CSV must contain column '{col}'.")
            has_file = "File" in df.columns
            options = []
            mapping = {}
            for _, row in df.iterrows():
                try:
                    session_start = parse_datetime(row["Session Start"])
                    session_end = parse_datetime(row["Session End"])
                    time_required = float(row["Time Required"])
                    file_val = row["File"] if has_file else None
                except Exception:
                    continue
                display = (f"{file_val} | " if file_val else "") + f"{session_start.strftime('%Y-%m-%d %H:%M:%S')} to {session_end.strftime('%Y-%m-%d %H:%M:%S')} ({time_required} min)"
                options.append(display)
                mapping[display] = (session_start, session_end, time_required, file_val)
            if not options:
                messagebox.showerror("Error", "No valid session configurations found in the CSV file.")
                return
            self.session_config_options = options
            self.session_config_mapping = mapping
            self.session_config_label.configure(state="normal")
            self.session_config_label.delete(0, tk.END)
            self.session_config_label.insert(0, os.path.basename(file_path))
            self.session_config_label.configure(state="readonly")
            for session_dict in self.session_rows:
                if "session_config_combobox" in session_dict:
                    session_dict["session_config_combobox"].set_completion_list(self.session_config_options)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session config CSV: {e}")

    def apply_session_config(self, config_var, start_entry, end_entry, time_required_entry, file_widget=None):
        selection = config_var.get()
        if selection in self.session_config_mapping:
            session_start, session_end, time_required, file_val = self.session_config_mapping[selection]
            start_entry.delete(0, tk.END)
            start_entry.insert(0, session_start.strftime('%Y-%m-%d %H:%M:%S'))
            end_entry.delete(0, tk.END)
            end_entry.insert(0, session_end.strftime('%Y-%m-%d %H:%M:%S'))
            time_required_entry.delete(0, tk.END)
            time_required_entry.insert(0, str(time_required))
            if file_widget and file_val:
                if isinstance(file_widget, ttk.Combobox):
                    if file_val in self.file_mapping:
                        file_widget.set(file_val)
                else:
                    file_widget.config(text=file_val)

    def add_session(self):
        mode = self.mode_mapping[self.mode_var.get()]
        row_frame = ttk.Frame(self.sessions_container)
        row_frame.pack(fill="x", pady=2)
        session_dict = {}
        if mode == "single":
            file_name = os.path.basename(self.selected_file) if self.selected_file else ""
            file_widget = ttk.Label(row_frame, text=file_name, width=20, anchor="w")
            file_widget.grid(row=0, column=0, padx=3)
            session_dict["file_widget"] = file_widget
            session_dict["file_path"] = self.selected_file
        else:
            file_options = list(self.file_mapping.keys())
            file_var = tk.StringVar(value=file_options[0] if file_options else "")
            file_widget = ttk.Combobox(row_frame, textvariable=file_var, values=file_options, state="readonly", width=18)
            file_widget.grid(row=0, column=0, padx=3)
            session_dict["file_widget"] = file_widget
            session_dict["file_var"] = file_var

        session_config_var = tk.StringVar()
        session_config_combobox = AutocompleteCombobox(row_frame, textvariable=session_config_var, state="readonly", width=28)
        if self.session_config_options:
            session_config_combobox.set_completion_list(self.session_config_options)
        session_config_combobox.grid(row=0, column=1, padx=3)

        start_entry = ttk.Entry(row_frame, width=20)
        start_entry.grid(row=0, column=2, padx=3)
        end_entry = ttk.Entry(row_frame, width=20)
        end_entry.grid(row=0, column=3, padx=3)
        time_required_entry = ttk.Entry(row_frame, width=20)
        time_required_entry.grid(row=0, column=4, padx=3)

        session_config_combobox.bind("<<ComboboxSelected>>", 
            lambda e, var=session_config_var, fw=session_dict["file_widget"], se=start_entry, ee=end_entry, tre=time_required_entry: 
                   self.apply_session_config(var, se, ee, tre, file_widget=fw))
        
        session_dict.update({
            "session_config_var": session_config_var,
            "session_config_combobox": session_config_combobox,
            "frame": row_frame,
            "start_entry": start_entry,
            "end_entry": end_entry,
            "time_required_entry": time_required_entry
        })
        remove_btn = ttk.Button(row_frame, text="-", width=3,
                                command=lambda: self.remove_session(row_frame, session_dict),
                                bootstyle=DANGER + "-outline")
        remove_btn.grid(row=0, column=5, padx=3)
        self.session_rows.append(session_dict)

    def remove_session(self, frame, session_dict):
        frame.destroy()
        if session_dict in self.session_rows:
            self.session_rows.remove(session_dict)

    def toggle_theme(self):
        self.current_theme = "darkly" if self.current_theme == "flatly" else "flatly"
        self.style.theme_use(self.current_theme)

    def generate_attendance(self):
        mode = self.mode_mapping[self.mode_var.get()]
        if (mode == "single" and not self.selected_file) or (mode == "multiple" and not self.selected_files) or not self.session_rows:
            messagebox.showerror("Error", "Please ensure a CSV file(s) and at least one session are selected.")
            return

        self.generate_button.config(state="disabled")
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.start()
        self.master.update_idletasks()

        def task():
            try:
                if mode == "single":
                    sessions_info = []
                    for sess in self.session_rows:
                        s_text = sess["start_entry"].get().strip()
                        e_text = sess["end_entry"].get().strip()
                        tr_text = sess["time_required_entry"].get().strip()
                        if not s_text or not e_text or not tr_text:
                            self.master.after(0, lambda: messagebox.showerror("Error", "Session details missing in one of the session rows."))
                            return
                        try:
                            s_dt = parse_datetime(s_text)
                            e_dt = parse_datetime(e_text)
                            time_req_val = float(tr_text)
                        except ValueError as ve:
                            self.master.after(0, lambda: messagebox.showerror("Error", f"Error in session details: {ve}"))
                            return
                        if s_dt >= e_dt:
                            self.master.after(0, lambda: messagebox.showerror("Error", "Session Start must be before Session End."))
                            return
                        sessions_info.append({
                            "session_start": s_dt,
                            "session_end": e_dt,
                            "time_required": time_req_val
                        })
                    try:
                        output_records, session_labels, session_summary = process_sessions_for_file(self.selected_file, sessions_info)
                    except ValueError as ve:
                        self.master.after(0, lambda: messagebox.showerror("Error", str(ve)))
                        return
                    try:
                        with open(self.selected_file, 'r', encoding='utf-8') as f:
                            sample = f.read(1024)
                            f.seek(0)
                            dialect = csv.Sniffer().sniff(sample)
                            raw_data = list(csv.reader(f, dialect))
                        raw_log_df = pd.DataFrame(raw_data)
                    except Exception as e:
                        self.master.after(0, lambda: messagebox.showerror("Error", f"Error reading raw log from '{self.selected_file}': {e}"))
                        return
                    base = os.path.basename(self.selected_file)
                    name_part, _ = os.path.splitext(base)
                    # Automatically use same folder and same name with suffix
                    output_file = os.path.join(os.path.dirname(self.selected_file), name_part + "_processed.xlsx")
                    try:
                        write_excel(raw_log_df, output_records, output_file)
                    except ValueError as e:
                        self.master.after(0, lambda: messagebox.showerror("Error", str(e)))
                        return
                    summary_str = "\n".join(session_summary)
                    self.master.after(0, lambda: messagebox.showinfo("Attendance Generated",
                                                    f"Attendance generated and saved to:\n{output_file}\n\nAttendance Summary:\n{summary_str}"))
                else:
                    sessions_by_file = {}
                    for sess in self.session_rows:
                        s_text = sess["start_entry"].get().strip()
                        e_text = sess["end_entry"].get().strip()
                        tr_text = sess["time_required_entry"].get().strip()
                        if not s_text or not e_text or not tr_text:
                            self.master.after(0, lambda: messagebox.showerror("Error", "Session details missing in one of the session rows."))
                            return
                        try:
                            s_dt = parse_datetime(s_text)
                            e_dt = parse_datetime(e_text)
                            time_req_val = float(tr_text)
                        except ValueError as ve:
                            self.master.after(0, lambda: messagebox.showerror("Error", f"Error in session details: {ve}"))
                            return
                        if s_dt >= e_dt:
                            self.master.after(0, lambda: messagebox.showerror("Error", "Session Start must be before Session End."))
                            return
                        file_name = sess["file_widget"].get() if mode == "multiple" else os.path.basename(self.selected_file)
                        if mode == "multiple" and file_name not in self.file_mapping:
                            self.master.after(0, lambda: messagebox.showerror("Error", f"Selected file '{file_name}' not found."))
                            return
                        file_path = self.file_mapping[file_name] if mode == "multiple" else self.selected_file
                        sessions_by_file.setdefault(file_path, []).append({
                            "session_start": s_dt,
                            "session_end": e_dt,
                            "time_required": time_req_val
                        })
                    if not sessions_by_file:
                        self.master.after(0, lambda: messagebox.showerror("Error", "No session information available."))
                        return
                    summary_all = {}
                    for file_path, sessions_info in sessions_by_file.items():
                        try:
                            output_records, session_labels, session_summary = process_sessions_for_file(file_path, sessions_info)
                        except ValueError as ve:
                            self.master.after(0, lambda: messagebox.showerror("Error", str(ve)))
                            return
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                sample = f.read(1024)
                                f.seek(0)
                                dialect = csv.Sniffer().sniff(sample)
                                raw_data = list(csv.reader(f, dialect))
                            raw_log_df = pd.DataFrame(raw_data)
                        except Exception as e:
                            self.master.after(0, lambda: messagebox.showerror("Error", f"Error reading raw log from '{file_path}': {e}"))
                            return
                        base = os.path.basename(file_path)
                        name_part, _ = os.path.splitext(base)
                        # Save automatically with suffix _processed.xlsx
                        output_file = os.path.join(os.path.dirname(file_path), name_part + "_processed.xlsx")
                        try:
                            write_excel(raw_log_df, output_records, output_file)
                        except ValueError as e:
                            self.master.after(0, lambda: messagebox.showerror("Error", f"Error saving output Excel file for {base}: {e}"))
                            return
                        summary_all[base] = "\n".join(session_summary)
                    summary_str = "\n\n".join([f"{fname}:\n{summary}" for fname, summary in summary_all.items()])
                    self.master.after(0, lambda: messagebox.showinfo("Attendance Generated",
                                                    f"Processed {len(summary_all)} files.\n\nAttendance Summary:\n{summary_str}"))
            finally:
                self.master.after(0, self.reset_generate_button)

        threading.Thread(target=task).start()

    def reset_generate_button(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.generate_button.config(state="normal")

# ====================================================
# Attendance Match Tool UI
# ====================================================

def show_attendance_match_tool():
    clear_content()
    match_frame = tk.Frame(content_frame, padx=20, pady=20, bg="#f5f5f5")
    match_frame.pack(fill="both", expand=True)

    # Mode Selection
    mode_frame = tk.Frame(match_frame, bg="#f5f5f5")
    mode_frame.pack(fill="x", pady=10)
    tk.Label(mode_frame, text="Select Mode:", font=("Helvetica", 12), bg="#f5f5f5").pack(side="left")
    match_mode = tk.StringVar(value="single")
    tk.Radiobutton(mode_frame, text="Single Excel", variable=match_mode, value="single",
                   font=("Helvetica", 12), bg="#f5f5f5").pack(side="left", padx=10)
    tk.Radiobutton(mode_frame, text="Multiple Excel", variable=match_mode, value="multiple",
                   font=("Helvetica", 12), bg="#f5f5f5").pack(side="left", padx=10)

    # File Selection
    file_frame = tk.Frame(match_frame, bg="#f5f5f5")
    file_frame.pack(fill="x", pady=10)
    tk.Label(file_frame, text="Select Excel File(s):", font=("Helvetica", 12), bg="#f5f5f5").pack(side="left")
    file_entry = tk.Entry(file_frame, width=50, font=("Helvetica", 12))
    file_entry.pack(side="left", padx=5)
    selected_files = []  # list to hold selected file paths

    def browse_files():
        nonlocal selected_files
        if match_mode.get() == "single":
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                selected_files = [file_path]
                file_entry.delete(0, tk.END)
                file_entry.insert(0, os.path.basename(file_path))
        else:
            files = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx")])
            if files:
                selected_files = list(files)
                file_entry.delete(0, tk.END)
                file_entry.insert(0, f"{len(selected_files)} file(s) selected")
    tk.Button(file_frame, text="Browse", command=browse_files, font=("Helvetica", 12)).pack(side="left")

    # Process Button
    process_button = tk.Button(match_frame, text="Process to match", font=("Helvetica", 12), width=20)
    process_button.pack(pady=10)

    # Progress Bar and Label
    progress_bar = ttk.Progressbar(match_frame, mode="determinate")
    progress_bar.pack(fill="x", pady=5)
    progress_label = tk.Label(match_frame, text="", font=("Helvetica", 12), bg="#f5f5f5")
    progress_label.pack()

    def process_match():
        if not selected_files:
            messagebox.showerror("Error", "Please select at least one Excel file.")
            return
        process_button.config(state="disabled")
        num_files = len(selected_files)
        progress_bar.config(maximum=num_files)
        progress_bar['value'] = 0
        results = {}  # to store processing time for each file

        def task():
            for i, file in enumerate(selected_files):
                progress_label.config(text=f"Processing: {os.path.basename(file)}")
                start_time = time.time()
                dir_name = os.path.dirname(file)
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_file = os.path.join(dir_name, base_name + "_processed_match_attendance.xlsx")
                try:
                    process_file_match(file, output_file, silent=True)
                except Exception as e:
                    match_frame.after(0, lambda: messagebox.showerror("Error", f"Error processing {os.path.basename(file)}: {e}"))
                    continue
                elapsed = time.time() - start_time
                results[file] = elapsed
                progress_bar['value'] = i + 1
            summary_lines = [f"{os.path.basename(f)}: {results[f]:.2f} seconds" for f in results]
            summary_text = "\n".join(summary_lines)
            match_frame.after(0, lambda: messagebox.showinfo("Processing Complete", f"Files processed:\n{summary_text}"))
            match_frame.after(0, lambda: progress_label.config(text="Processing complete"))
            match_frame.after(0, lambda: process_button.config(state="normal"))

        threading.Thread(target=task).start()

    process_button.config(command=process_match)

    # Back Button
    tk.Button(match_frame, text="Back", command=show_main_menu, font=("Helvetica", 12)).pack(pady=10)

# ====================================================
# Navigation Functions for Main Window
# ====================================================

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_main_menu():
    clear_content()
    main_menu = tk.Frame(content_frame, bg="#f5f5f5")
    main_menu.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Header section
    header = tk.Frame(main_menu, bg="#4a90e2")
    header.pack(fill="x", pady=(0,20))
    title = tk.Label(header, text="Attendance Tools Dashboard", font=("Helvetica", 24, "bold"), bg="#4a90e2", fg="white")
    title.pack(pady=10)
    
    # Button section
    btn_frame = tk.Frame(main_menu, bg="#f5f5f5")
    btn_frame.pack(pady=10)
    
    btn_generator = tk.Button(btn_frame, text="Attendance Generator from ZOOM log", command=show_attendance_generator, 
                              width=40, height=2, bg="#4a90e2", fg="white", font=("Helvetica", 14, "bold"), bd=0)
    btn_generator.pack(pady=10)
    
    btn_match = tk.Button(btn_frame, text="Attendance Match Tool", command=show_attendance_match_tool, 
                          width=40, height=2, bg="#4a90e2", fg="white", font=("Helvetica", 14, "bold"), bd=0)
    btn_match.pack(pady=10)
    
    # Instructions area
    instructions = (
        "Instructions:\n\n"
        "1. Attendance Generator:\n"
        "   - Process Zoom attendance logs and generate an Excel report with detailed attendance.\n"
        "   - Load the CSV log file, configure sessions, and click 'Generate Attendance'.\n\n"
        "2. Attendance Match Tool:\n"
        "   - Match names from a main list with Zoom log names.\n"
        "   - Select an Excel file (or multiple files) and click 'Process to match' to automatically save matched results.\n"
        "\nSelect the desired tool by clicking the corresponding button above."
    )
    instr_frame = tk.Frame(main_menu, bg="#f5f5f5")
    instr_frame.pack(pady=20, fill="both", expand=True)
    instr_text = tk.Text(instr_frame, wrap="word", font=("Helvetica", 12), bg="white", bd=1, relief="solid")
    instr_text.pack(fill="both", expand=True)
    instr_text.insert("1.0", instructions)
    instr_text.config(state="disabled")

def show_attendance_generator():
    clear_content()
    gen_frame = tk.Frame(content_frame)
    gen_frame.pack(fill="both", expand=True)
    AttendanceGeneratorApp(gen_frame, back_callback=show_main_menu)

# ====================================================
# Main Application Startup
# ====================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Combined Attendance Tools")
    root.geometry("800x600")

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    show_main_menu()

    root.mainloop()
