# Attendancify

**Professional Attendance Management Made Simple**

[Live Deployment](https://aiattendance.pythonanywhere.com/)

## Overview

Attendancify is a comprehensive, web-based suite designed to streamline and automate attendance management. Tailored for educators, trainers, and event organizers, it helps transform raw attendance data—especially Zoom meeting logs—into structured, actionable insights with minimal effort. The platform offers fast, reliable, and smart tools for generating, matching, and exporting attendance records.

## Features

### Dashboard
One-stop hub with access to all core tools and quick navigation.

### Attendance Generator
Upload and process multiple Zoom attendance CSV logs. Configure time/session requirements, generate Excel attendance reports marking each participant Present/Absent.

### Raw Excel Generator
Transform messy or irregular Excel attendance data into standardized raw format, ready for analysis. Ideal for batch processing and clean data exports.

### Attendance Matching
Compare and reconcile attendance from disparate sources using intelligent, fuzzy name-matching algorithms, ensuring robust participant tracking across lists.

### Fast Processing
Capable of handling large files and complex datasets using optimized back-end routines.

### Smart Matching
Advanced algorithms for robust, error-tolerant data matching.

### Clean Reports
Exports structured Excel sheets, suitable for academic, corporate, or administrative records.

## How It Works

### Attendance Generator
1. **Upload**: Select and upload multiple Zoom attendance CSV files.
2. **Configure**: Set minimum required attendance durations or other criteria per session.
3. **Process & Export**: Generate Excel reports with automatically computed attendance statuses (Present/Absent).

**Instructions:**
- Upload your CSV Zoom reports
- Optionally adjust session requirements
- Download generated Excel files for each session—ready for use or submission

### Raw Excel Generator
- Upload Excel attendance sheets (any format)
- Transform into a standardized raw Excel file for consistent record-keeping

### Attendance Matching
- Upload two or more attendance source files
- Run the smart matching process to reconcile names and generate a unified report

## Getting Started

### Clone this repository
```bash
git clone https://github.com/satendravoice/attendancify.git
cd attendancify
```

### Set up Python environment & dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure
Update configuration files (config.py or .env) as needed for deployment

### Run Locally
```bash
flask run
```

### Deploy
Can be easily hosted on platforms like PythonAnywhere

## Use Cases

- Educational institutions automating Zoom/online class attendance
- Corporate HR teams tracking training/event participation
- Trainers, coaches, and webinars with large rosters
- Any scenario needing hassle-free, scalable attendance management

## Tech Stack

- **Python (Flask)**
- **Pandas, openpyxl** (for data processing)
- **Front-end**: HTML/CSS (with a clean, professional UI)

## Credits

**Developer**: [Satendra Goswami](https://www.instagram.com/satendragoswamii/)

Project and code licensed under the MIT License

## Screenshots

Consider adding here: Home page, Attendance Generator workflow, Raw Excel output, and Matching result screenshots.

## License

Distributed under the MIT License. See LICENSE for more information.

---

### Notes for enhancement:
- Add screenshots for each major workflow
- Include sample input/output files in /examples
- Expand Usage section with batch automation if supported
- Provide Contributions/Issues/Feature request guidelines
