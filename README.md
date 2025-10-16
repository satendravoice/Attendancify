# Attendancify – Attendance Tools Suite

Automated, accurate attendance management for modern education.

## 🚀 Live Demo

[Try it now](https://aiattendance.pythonanywhere.com)

## Overview

Attendancify automates attendance tracking for Zoom sessions. It processes session logs with second-level precision and customizable time thresholds to generate accurate attendance records.

## Key Features

- **Automatic Attendance Generation**: Creates verified attendance records from Zoom logs
- **Second-Level Precision**: Calculates presence duration down to the second
- **Master Sheet Matching**: Cross-matches attendance with student lists
- **Batch Processing**: Handles multiple sessions efficiently
- **Intelligent Name Matching**: Uses fuzzy algorithms to handle name variations
- **Customizable Thresholds**: Set time requirements for attendance marking

## Tech Stack

- Python 3.9+, Flask
- Pandas for data processing
- OpenPyXL for Excel operations
- RapidFuzz for name matching
- Bootstrap 5 for UI

## Quick Start

```bash
# Clone the repo
git clone https://github.com/satendravoice/Attendancify.git
cd Attendancify

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python comprehensive_app.py
```

Visit `http://localhost:5000` in your browser.

## Usage

### 1. Attendance Generation
1. Upload Zoom session log (CSV)
2. Configure time thresholds
3. Generate and download attendance report

### 2. Master Sheet Matching
1. Upload attendance file and student master list
2. System performs intelligent matching
3. Download comprehensive report

### 3. Raw Excel Generator
1. Upload Excel files with attendance data
2. Extract and format raw attendance
3. Download processed files

## File Formats and Parameters

### 1. Attendance Generator

**Input File Format (CSV):**
- Must be a Zoom meeting attendance report
- Required columns:
  - `Name` (or `Name (Original Name)`)
  - `User Email`
  - `Join Time` (or `Join time`) - Format: `YYYY-MM-DD HH:MM:SS`
  - `Leave Time` (or `Leave time`) - Format: `YYYY-MM-DD HH:MM:SS`
  - `Duration` (or `Duration (minutes)`) - In minutes

**Parameters:**
- Session start time (datetime)
- Session end time (datetime)
- Minimum required time (minutes) - Default: 30 minutes

**Output:**
- Excel file with two sheets:
  - Original log data
  - Processed attendance with status (P/A) for each session

### 2. Master Sheet Matching

**Input File Formats:**

*Attendance File (CSV/Excel):*
- Must contain a `Name` column
- Additional columns represent session attendance (P/A status)

*Master List File (CSV/Excel):*
- Required columns:
  - `Participant Name` (or `Name`)
  - `Email` (or `Email_id`)
- Optional columns:
  - Student ID
  - Any other identifying information

**Parameters:**
- Matching threshold (fuzzy matching sensitivity) - Default: 85%
- Output format (CSV or Excel) - Default: Excel

**Output:**
- Excel file with three sheets:
  - `Matched`: Master list with attendance status
  - `Unmatched Raw`: Entries from attendance file not found in master list
  - `Summary`: Attendance summary

### 3. Raw Excel Generator

**Input File Format (Excel):**
- Must contain a sheet named `Attendance`
- Must have a `Name` column (or `Participant Name`)
- Session columns with P/A values

**Parameters:**
- None required (fully automated)

**Output:**
- Excel file with standardized format
- Columns: Name and session attendance (P/A status)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to branch
5. Open a pull request

## License

[MIT License](LICENSE)

## Developed by

[Satendra Goswami](https://www.instagram.com/satendragoswamii/)

© 2025 Attendancify
