# Attendancify – Attendance Tools Suite
Automated, accurate attendance management for modern education

## 🚀 Live Demo
Try it now: https://attendancify.pythonanywhere.com

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
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Generate Attendance from Zoom Logs
1. Click "Generate Attendance" from the main menu.
2. Upload your Zoom session log (Excel format).
3. Enter the required session duration (in minutes or seconds).
4. Submit to generate the attendance report.
5. Download the processed Excel file with attendance data.

### Check for Absent Students
1. Click "Check Absentees" from the main menu.
2. Upload your session attendance file (generated in step above).
3. Upload your master student list (Excel format).
4. Submit to cross-match participants with enrolled students.
5. Download the Excel file listing students who were absent from the session.

## File Formats

### Zoom Session Log
- Must be an Excel file (.xlsx)
- Should contain columns for participant names and session duration
- Exported directly from Zoom after a session

### Master Student List
- Must be an Excel file (.xlsx)
- Should contain a column with student names (exact match with Zoom log names)
- Represents the official enrollment list

## Features in Detail

### Automatic Attendance Generation
- Parses Zoom session logs
- Calculates total time each participant was present
- Compares against admin-defined threshold
- Marks participants as Present or Absent
- Exports results to Excel

### Master Sheet Matching
- Cross-references session attendance with enrollment list
- Identifies students who didn't attend at all
- Produces a comprehensive absentee report
- Useful for compliance and follow-up communication

### Customizable Thresholds
- Admins can set minimum required session time
- Flexible to accommodate different class lengths
- Ensures fairness and consistency in attendance rules

## Deployment

This application is deployed on PythonAnywhere. To deploy your own instance:

1. Create a PythonAnywhere account
2. Upload your project files
3. Configure a web app with Flask
4. Set the working directory and WSGI configuration
5. Reload the web app

Refer to [PythonAnywhere documentation](https://help.pythonanywhere.com/) for detailed deployment steps.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

Please ensure your code follows best practices and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:
- Open an issue on [GitHub](https://github.com/satendravoice/Attendancify/issues)
- Contact: [Your Email or Support Channel]

## Acknowledgments

- Inspired by the need for efficient attendance management in remote education
- Built with open-source tools and frameworks
- Thanks to all contributors and users for their feedback

---

**Developed by:** Satendra Goswami
