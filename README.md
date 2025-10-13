# Attendancify – Attendance Tools Suite
Automated, accurate attendance management for modern education

## 🚀 Live Demo
Try it now: https://aiattendance.pythonanywhere.com/attendance_matching

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
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python comprehensive_app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

### Attendance Generation
1. Upload your Zoom session log (CSV format)
2. Set the minimum time threshold (in minutes) for marking attendance
3. Click Generate to process the file
4. Download the attendance report as an Excel file

### Master Sheet Matching
1. Upload the Zoom attendance file and your master student list
2. Map the columns (Name, Email, etc.) from both files
3. The tool will cross-match and generate a report showing:
   - Students who attended
   - Students who were absent
   - Any discrepancies or unmatched entries

## File Formats

### Zoom Log Format
The Zoom attendance report should be a CSV file with columns:
- Name (First Name)
- User Name (Display Name)
- User Email
- Join Time
- Leave Time
- Duration (Minutes)

### Master List Format
Your master student list should be an Excel file (.xlsx) with columns such as:
- Student Name
- Email Address
- Student ID (optional)
- Any other identifying information

## Features in Detail

### Intelligent Name Matching
The system uses fuzzy matching algorithms to handle:
- Name variations (e.g., "John Smith" vs "Smith, John")
- Nicknames and shortened names
- Minor spelling differences
- Email domain matching for verification

### Customizable Thresholds
Set your own criteria for attendance:
- Minimum session duration required
- Late arrival tolerance
- Early departure allowance

### Comprehensive Reports
Generated reports include:
- Individual attendance status
- Total time spent in session
- Entry and exit timestamps
- Attendance percentage calculations

## Deployment

The application is deployed on PythonAnywhere. To deploy your own instance:

1. Create a PythonAnywhere account
2. Upload your code via Git or file upload
3. Configure the WSGI file (wsgi.py is included)
4. Set up the web app in the dashboard
5. Install dependencies using the bash console

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## Acknowledgments

- Built with Flask and Python
- Uses Pandas for efficient data processing
- Bootstrap for responsive design
- Inspired by the need for accurate remote attendance tracking

## Developed by

Developed by: [Satendra Goswami](https://instagram.com/satendragoswamii)
