from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
import os
import pandas as pd
from datetime import datetime
import io
import tempfile
import csv
import re
import zipfile
from rapidfuzz import fuzz
from werkzeug.utils import secure_filename

# Import the core processing functions from the new module
from attendance_processing import (
    process_sessions_for_file, parse_datetime, write_excel
)

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key_here'  # Change this in production

# Directory for temporary files
TEMP_DIR = tempfile.gettempdir()

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# ----------- Name Normalization -----------
def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip().lower()

# ----------- Raw Excel Generator Functions -----------
SHEET_NAME = "Attendance"

def extract_raw_from_excel(xl_path):
    # Always extract sheet named "Attendance"
    xl = pd.ExcelFile(xl_path)
    if SHEET_NAME not in xl.sheet_names:
        raise ValueError(f"Sheet '{SHEET_NAME}' not found in the file.")
    df = xl.parse(SHEET_NAME)
    name_col = next((c for c in df.columns if str(c).strip().lower() in ("name", "participant name")), None)
    if not name_col:
        raise ValueError("No 'Name' column found.")
    session_cols = [c for c in df.columns if str(df[c].dropna().unique()).strip("[]").replace("'", "").lower() in ("p, a", "p", "a")]
    # Fallback for cases session columns have headers with "Session" or contain P/A markers
    if not session_cols:
        session_cols = [c for c in df.columns if "session" in str(c).lower()]
    out = df[[name_col]+session_cols].copy()
    out.columns = ["Name"] + [str(c) for c in session_cols]
    # Only keep "P"/"A", replace anything else with "N/A"
    for col in session_cols:
        out[col] = out[col].apply(lambda x: x if str(x).strip().upper() in ("P","A") else "N/A")
    return out

# ----------- Attendance Matching Functions -----------
def read_raw_file(raw_path: str) -> pd.DataFrame:
    df = pd.read_csv(raw_path) if raw_path.lower().endswith(".csv") else pd.read_excel(raw_path)
    df.columns = [str(c).strip() for c in df.columns]
    name_col = next((c for c in df.columns if c.lower() in ("name", "participant name")), None)
    if name_col is None:
        raise ValueError("Raw file needs a 'Name' column.")
    session_cols = [c for c in df.columns if c != name_col]
    if not session_cols:
        raise ValueError("Raw file contains no session/status columns.")
    def norm(x): return x if str(x) in ("P", "A") else "N/A"
    for col in session_cols:
        df[col] = df[col].apply(norm)
    out = df[[name_col] + session_cols].copy()
    out.columns = ["Name"] + session_cols
    return out

def postprocess_attendance(df, session_cols):
    # Replace P→present, A→absent (case-insensitive), but only in session columns
    for col in session_cols:
        df[col] = df[col].replace({"P": "present", "A": "absent", "p": "present", "a": "absent"})
    return df

def match_and_write(master_file: str, raw_file: str, out_fmt: str = "xlsx") -> str:
    mdf = pd.read_csv(master_file) if master_file.lower().endswith(".csv") else pd.read_excel(master_file)
    email_col = next((c for c in mdf.columns if str(c).strip().lower() in ("email", "email_id")), None)
    name_col = next((c for c in mdf.columns if str(c).strip().lower() in ("participant name", "name")), None)
    if email_col is None or name_col is None:
        raise ValueError("Master file must have 'Email' and 'Participant Name' columns.")
    mdf = mdf[[email_col, name_col]].copy()
    mdf.columns = ["Email", "Participant Name"]
    rdf = read_raw_file(raw_file)
    session_cols = list(rdf.columns[1:])
    raw_norm_names = [normalize_name(n) for n in list(rdf["Name"])]
    matched_df = mdf.copy()
    for col in session_cols:
        matched_df[col] = "N/A"
    threshold = 85
    matched_indices = set()
    for idx, row in matched_df.iterrows():
        master_name = normalize_name(str(row["Participant Name"]))
        best_score, best_j = -1, None
        for j, raw_norm in enumerate(raw_norm_names):
            score = fuzz.token_set_ratio(master_name, raw_norm)
            if score > best_score:
                best_score = score
                best_j = j
        if best_score >= threshold:
            raw_row = rdf.iloc[best_j]
            for col in session_cols:
                matched_df.at[idx, col] = raw_row[col]
            matched_indices.add(best_j)
    unmatched_df = rdf.iloc[[i for i in range(len(rdf)) if i not in matched_indices]].copy()
    if not unmatched_df.empty:
        unmatched_df.rename(columns={"Name": "Raw Name (not found in Master)"}, inplace=True)
    # ---- Here: replace P/A
    matched_df = postprocess_attendance(matched_df, session_cols)
    if not unmatched_df.empty:
        unmatched_df = postprocess_attendance(unmatched_df, session_cols)
    out_dir = os.path.dirname(master_file)
    mbase = os.path.splitext(os.path.basename(master_file))[0]
    rbase = os.path.splitext(os.path.basename(raw_file))[0]
    if out_fmt == "xlsx":
        out_path = os.path.join(out_dir, f"{mbase}_matched_with_{rbase}_attendance.xlsx")
        with pd.ExcelWriter(out_path, engine="openpyxl") as w:
            matched_df.to_excel(w, index=False, sheet_name="Matched")
            if not unmatched_df.empty:
                unmatched_df.to_excel(w, index=False, sheet_name="Unmatched Raw")
            pd.DataFrame([], columns=["email_id", "attendance(absent/present/leave)"]).to_excel(w, index=False, sheet_name="Summary")
        return out_path
    prefix = os.path.join(out_dir, f"{mbase}_matched_with_{rbase}_")
    matched_df.to_csv(prefix + "matched.csv", index=False)
    if not unmatched_df.empty:
        unmatched_df.to_csv(prefix + "unmatched.csv", index=False)
    pd.DataFrame([], columns=["email_id", "attendance(absent/present/leave)"]).to_csv(prefix + "summary.csv", index=False)
    return prefix + "matched.csv"

# ----------- Routes -----------
@app.route('/')
def index():
    return render_template('comprehensive_index.html')

# ----------- Attendance Generator Routes -----------
@app.route('/attendance_generator')
def attendance_generator():
    return render_template('attendance_generator.html')

@app.route('/upload_attendance', methods=['POST'])
def upload_attendance_file():
    # Get the mode (single or multiple)
    mode = request.form.get('mode', 'single')
    
    if mode == 'single':
        if 'csv_file' not in request.files:
            flash('No file selected')
            return redirect(url_for('attendance_generator'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('attendance_generator'))
        
        if file:
            # Save file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(TEMP_DIR, filename)
            file.save(file_path)
            
            # Store file info in session
            session['file_path'] = file_path
            session['filename'] = filename
            session['mode'] = 'single'
            
            return redirect(url_for('configure_attendance_sessions'))
    else:  # multiple mode
        files = request.files.getlist('csv_files')
        if not files or not any(f.filename for f in files):
            flash('No files selected')
            return redirect(url_for('attendance_generator'))
        
        # Save all files
        file_paths = []
        file_names = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(TEMP_DIR, filename)
                file.save(file_path)
                file_paths.append(file_path)
                file_names.append(filename)
        
        # Store file info in session
        session['file_paths'] = file_paths
        session['file_names'] = file_names
        session['mode'] = 'multiple'
        
        return redirect(url_for('configure_attendance_sessions'))

@app.route('/configure_attendance_sessions')
def configure_attendance_sessions():
    mode = session.get('mode', 'single')
    if mode == 'single':
        return render_template('configure_attendance.html', mode='single')
    else:
        file_names = session.get('file_names', [])
        return render_template('configure_attendance.html', mode='multiple', file_names=file_names)

@app.route('/process_attendance', methods=['POST'])
def process_attendance():
    try:
        mode = session.get('mode', 'single')
        
        if mode == 'single':
            # Get session data
            file_path = session.get('file_path')
            if not file_path or not os.path.exists(file_path):
                flash('File not found. Please upload again.')
                return redirect(url_for('attendance_generator'))
            
            # Get session configurations from form
            sessions_info = []
            session_count = int(request.form.get('session_count', 0))
            
            for i in range(session_count):
                start_str = request.form.get(f'start_time_{i}')
                end_str = request.form.get(f'end_time_{i}')
                time_required = float(request.form.get(f'time_required_{i}', 30))
                
                if start_str and end_str:
                    # Convert datetime-local format to our expected format
                    session_start = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
                    session_end = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
                    
                    if session_start >= session_end:
                        flash(f'Error in session {i+1}: Start time must be before end time.')
                        return redirect(url_for('configure_attendance_sessions'))
                    
                    sessions_info.append({
                        "session_start": session_start,
                        "session_end": session_end,
                        "time_required": time_required
                    })
            
            if not sessions_info:
                flash('Please add at least one session.')
                return redirect(url_for('configure_attendance_sessions'))
            
            # Process the attendance
            output_records, session_labels, session_summary = process_sessions_for_file(file_path, sessions_info)
            
            # Read raw log data
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                raw_data = list(csv.reader(f, dialect))
            raw_log_df = pd.DataFrame(raw_data)
            
            # Create output Excel file
            output_filename = os.path.splitext(session['filename'])[0] + '_processed.xlsx'
            output_path = os.path.join(TEMP_DIR, output_filename)
            
            write_excel(raw_log_df, output_records, output_path)
            
            # Store output path in session
            session['output_path'] = output_path
            session['output_filename'] = output_filename
            
            return redirect(url_for('download_attendance'))
        else:  # multiple mode
            file_paths = session.get('file_paths', [])
            file_names = session.get('file_names', [])
            
            if not file_paths:
                flash('No files found. Please upload again.')
                return redirect(url_for('attendance_generator'))
            
            # Get session configurations from form
            # In multiple mode, we need to associate sessions with specific files
            sessions_by_file = {}
            
            # Get the number of session rows
            session_row_count = int(request.form.get('session_row_count', 0))
            
            for i in range(session_row_count):
                file_name = request.form.get(f'file_name_{i}')
                start_str = request.form.get(f'start_time_{i}')
                end_str = request.form.get(f'end_time_{i}')
                time_required = float(request.form.get(f'time_required_{i}', 30))
                
                if file_name and start_str and end_str:
                    # Convert datetime-local format to our expected format
                    session_start = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
                    session_end = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
                    
                    if session_start >= session_end:
                        flash(f'Error in session for file {file_name}: Start time must be before end time.')
                        return redirect(url_for('configure_attendance_sessions'))
                    
                    # Find the file path for this file name
                    file_path = None
                    for j, name in enumerate(file_names):
                        if name == file_name:
                            file_path = file_paths[j]
                            break
                    
                    if file_path:
                        session_info = {
                            "session_start": session_start,
                            "session_end": session_end,
                            "time_required": time_required
                        }
                        
                        if file_path not in sessions_by_file:
                            sessions_by_file[file_path] = {
                                "file_name": file_name,
                                "sessions": []
                            }
                        
                        sessions_by_file[file_path]["sessions"].append(session_info)
            
            if not sessions_by_file:
                flash('Please add at least one session.')
                return redirect(url_for('configure_attendance_sessions'))
            
            # Process each file
            output_files = []
            summary_all = {}
            
            for file_path, file_data in sessions_by_file.items():
                file_name = file_data["file_name"]
                sessions_info = file_data["sessions"]
                
                try:
                    # Process the attendance
                    output_records, session_labels, session_summary = process_sessions_for_file(file_path, sessions_info)
                    
                    # Read raw log data
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sample = f.read(1024)
                        f.seek(0)
                        dialect = csv.Sniffer().sniff(sample)
                        raw_data = list(csv.reader(f, dialect))
                    raw_log_df = pd.DataFrame(raw_data)
                    
                    # Create output Excel file
                    output_filename = os.path.splitext(file_name)[0] + '_processed.xlsx'
                    output_path = os.path.join(TEMP_DIR, output_filename)
                    
                    write_excel(raw_log_df, output_records, output_path)
                    
                    output_files.append({
                        'path': output_path,
                        'name': output_filename
                    })
                    
                    summary_all[file_name] = "\n".join(session_summary)
                except Exception as e:
                    flash(f'Error processing file {file_name}: {str(e)}')
                    return redirect(url_for('configure_attendance_sessions'))
            
            # Store output files in session
            session['attendance_output_files'] = output_files
            
            return redirect(url_for('download_attendance'))
        
    except Exception as e:
        flash(f'Error processing attendance: {str(e)}')
        return redirect(url_for('configure_attendance_sessions'))

@app.route('/download_attendance')
def download_attendance():
    mode = session.get('mode', 'single')
    
    if mode == 'single':
        output_path = session.get('output_path')
        output_filename = session.get('output_filename')
        
        if not output_path or not os.path.exists(output_path):
            flash('Processed file not found.')
            return redirect(url_for('attendance_generator'))
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    else:
        output_files = session.get('attendance_output_files', [])
        
        # Check if a specific file is requested
        requested_file = request.args.get('file')
        if requested_file:
            for file_info in output_files:
                if file_info['name'] == requested_file:
                    return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
        
        if not output_files:
            flash('No processed files found.')
            return redirect(url_for('attendance_generator'))
        
        # If only one file, download it directly
        if len(output_files) == 1:
            file_info = output_files[0]
            return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
        else:
            # Render template to show all files
            return render_template('download_attendance.html', files=output_files)

# ----------- Raw Excel Generator Routes -----------
@app.route('/raw_excel_generator')
def raw_excel_generator():
    return render_template('raw_excel_generator.html')

@app.route('/process_raw_excel', methods=['POST'])
def process_raw_excel():
    try:
        # Get uploaded files
        files = request.files.getlist('excel_files')
        if not files or not any(f.filename for f in files):
            flash('No files selected')
            return redirect(url_for('raw_excel_generator'))
        
        # Process each file
        output_files = []
        for file in files:
            if file.filename:
                # Save file temporarily
                filename = secure_filename(file.filename)
                file_path = os.path.join(TEMP_DIR, filename)
                file.save(file_path)
                
                # Process the file
                raw_df = extract_raw_from_excel(file_path)
                
                # Create output file
                output_filename = os.path.splitext(filename)[0] + '-RAW.xlsx'
                output_path = os.path.join(TEMP_DIR, output_filename)
                raw_df.to_excel(output_path, index=False)
                
                output_files.append({
                    'path': output_path,
                    'name': output_filename
                })
        
        # Store output files in session
        session['raw_output_files'] = output_files
        
        return redirect(url_for('download_raw_excel'))
        
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(url_for('raw_excel_generator'))

@app.route('/download_raw_excel')
def download_raw_excel():
    output_files = session.get('raw_output_files', [])
    
    # Check if a specific file is requested
    requested_file = request.args.get('file')
    if requested_file:
        for file_info in output_files:
            if file_info['name'] == requested_file:
                return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
    
    if not output_files:
        flash('No processed files found.')
        return redirect(url_for('raw_excel_generator'))
    
    # If only one file, download it directly
    if len(output_files) == 1:
        file_info = output_files[0]
        return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
    else:
        # Create a zip file with all outputs
        zip_filename = 'raw_excel_files.zip'
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_info in output_files:
                zipf.write(file_info['path'], file_info['name'])
        
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

# ----------- Attendance Matching Routes -----------
@app.route('/attendance_matching')
def attendance_matching():
    return render_template('attendance_matching.html')

@app.route('/process_attendance_matching', methods=['POST'])
def process_attendance_matching():
    try:
        # Get uploaded files
        master_files = request.files.getlist('master_files')
        raw_files = request.files.getlist('raw_files')
        
        if not master_files or not raw_files:
            flash('Please select both master and raw files')
            return redirect(url_for('attendance_matching'))
        
        # Get output format
        output_format = request.form.get('output_format', 'xlsx')
        
        # Save master files
        master_file_paths = []
        master_file_names = []
        for file in master_files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(TEMP_DIR, filename)
                file.save(file_path)
                master_file_paths.append(file_path)
                master_file_names.append(filename)
        
        # Save raw files
        raw_file_paths = []
        raw_file_names = []
        for file in raw_files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(TEMP_DIR, filename)
                file.save(file_path)
                raw_file_paths.append(file_path)
                raw_file_names.append(filename)
        
        # Process file pairs
        output_files = []
        
        # Match files by index (first master with first raw, etc.)
        max_pairs = min(len(master_file_paths), len(raw_file_paths))
        
        for i in range(max_pairs):
            master_path = master_file_paths[i]
            master_name = master_file_names[i]
            raw_path = raw_file_paths[i]
            raw_name = raw_file_names[i]
            
            # Process the matching
            output_path = match_and_write(master_path, raw_path, output_format)
            
            output_files.append({
                'path': output_path,
                'name': os.path.basename(output_path)
            })
        
        # Store output files in session
        session['matching_output_files'] = output_files
        
        return redirect(url_for('download_attendance_matching'))
        
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        return redirect(url_for('attendance_matching'))

@app.route('/download_attendance_matching')
def download_attendance_matching():
    output_files = session.get('matching_output_files', [])
    
    # Check if a specific file is requested
    requested_file = request.args.get('file')
    if requested_file:
        for file_info in output_files:
            if file_info['name'] == requested_file:
                return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
    
    if not output_files:
        flash('No processed files found.')
        return redirect(url_for('attendance_matching'))
    
    # If only one file, download it directly
    if len(output_files) == 1:
        file_info = output_files[0]
        return send_file(file_info['path'], as_attachment=True, download_name=file_info['name'])
    else:
        # Create a zip file with all outputs
        zip_filename = 'matching_results.zip'
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_info in output_files:
                zipf.write(file_info['path'], file_info['name'])
        
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

if __name__ == '__main__':
    print("Starting Attendance Tools Suite...")
    print("Open your web browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0')