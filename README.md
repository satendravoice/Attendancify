# Attendancify – Attendance Tools Suite
Automated, accurate attendance management for modern education
## 🚀 Live Demo
Try it now: https://aiattendance.pythonanywhere.com
## Overview
Attendancify is designed for educators and organizations conducting online classes via Zoom. The app automates attendance tracking by processing Zoom session logs, calculating each participant's presence based on their precise session duration. Administrators can set custom time thresholds to specify how much time is needed to be marked present—ensuring exact and error-free attendance calculation.
Key features:
- *Automatic Attendance Generation*: Instantly creates verified attendance records from Zoom logs, with time criteria customizable by the admin.
- *Second-Level Precision*: Checks each participant's session duration down to the second, eliminating manual calculation errors.
- *Master Sheet Matching Tool*: Cross-matches session attendance with a master student list. Quickly identifies which enrolled students missed the session for easy reporting and compliance.
- *Batch Processing*: Runs on multiple sessions or files efficiently.
This suite streamlines reporting, enhances accuracy, and saves time for instructors and admins managing digital learning environments.
## Tech Stack
- Python 3.9+
- Flask: Web framework for the application interface
- Pandas: Data processing and analysis of attendance records
- OpenPyXL: Excel file handling for session logs and master lists
- Bootstrap 5: Responsive UI design
## Installation
### Prerequisites
- Python 3.9 or higher
- pip package manager
### Setup Steps
1. Clone the repository:
```bash
git clone https://github.com/satendravoice/Attendancify.git
cd Attendancify
```
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
