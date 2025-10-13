import os
import csv
import math
from datetime import datetime, timedelta
import pandas as pd

# ====================================================
# Helper Functions
# ====================================================

def format_time(time_in_minutes):
    """Converts a float (minutes) to a string 'M minutes S seconds'."""
    minutes = int(math.floor(time_in_minutes))
    seconds = int(round((time_in_minutes - minutes) * 60))
    return f"{minutes} minutes {seconds} seconds"

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