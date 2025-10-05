# Attendance Tools Suite

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green)](https://palletsprojects.com/p/flask/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive web application that integrates all attendance-related tools into a single interface. Process Zoom attendance logs, extract attendance data from Excel files, and match attendance records from different sources - all in one place.

## 🌟 Features

### 1. Attendance Generator
Process Zoom attendance logs and generate Excel reports with attendance status (Present/Absent) based on configurable session requirements.

- Support for single CSV file with multiple sessions
- Support for multiple CSV files processing
- Configurable session times and minimum attendance requirements
- Excel report generation with detailed attendance information

### 2. Raw Excel Generator
Extract attendance data from Excel files and generate standardized raw attendance files.

- Process multiple Excel files simultaneously
- Extract data from "Attendance" sheets
- Standardize attendance formats (P/A)
- Generate clean, structured attendance files

### 3. Attendance Matching
Match attendance data from different sources using intelligent name matching algorithms.

- Match multiple master files with multiple raw attendance files
- Intelligent fuzzy name matching
- Support for both Excel and CSV output formats
- Generate matched and unmatched reports

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/attendance-tools-suite.git
   cd attendance-tools-suite
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python comprehensive_app.py
   ```

4. **Access the application:**
   Open your web browser and navigate to `http://localhost:5000`

## 📖 Usage Instructions

### Attendance Generator
1. Choose between "Single CSV File" or "Multiple CSV Files" mode
2. Upload your Zoom attendance CSV file(s)
3. Configure session times and requirements
4. Process attendance data
5. Download Excel reports

### Raw Excel Generator
1. Upload one or more Excel files containing attendance data
2. The tool extracts data from the "Attendance" sheet
3. Standardized raw attendance files are generated
4. Download processed files

### Attendance Matching
1. Upload master file(s) containing participant names and email addresses
2. Upload raw attendance file(s) to match with master files
3. Files are matched in order (1st master with 1st raw, etc.)
4. Select output format (Excel or CSV)
5. Download matching results

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Data Processing**: pandas, openpyxl
- **Name Matching**: rapidfuzz
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **UI Components**: Font Awesome icons

## 📁 Project Structure

```
attendance-tools-suite/
├── comprehensive_app.py          # Main Flask application
├── attendance_magic.py           # Original attendance processing logic
├── Raw Excel Generator App.py    # Raw Excel generator logic
├── standalone_matchtool1.py      # Attendance matching logic
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore file
├── LICENSE                      # MIT License
├── README.md                    # This file
├── HOW_TO_RUN.md                # Detailed running instructions
├── templates/                   # HTML templates
│   ├── base_comprehensive.html   # Base template
│   ├── comprehensive_index.html  # Homepage
│   ├── attendance_generator.html # Attendance Generator UI
│   ├── configure_attendance.html # Session configuration
│   ├── raw_excel_generator.html  # Raw Excel Generator UI
│   ├── attendance_matching.html  # Attendance Matching UI
│   ├── download_attendance.html  # Attendance results
│   ├── download_raw_excel.html   # Raw Excel results
│   └── download_matching.html    # Matching results
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Satendra Goswami**
- Instagram: [@satendragoiswamii](https://www.instagram.com/satendragoiswamii)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped with the development
- Inspired by the need for efficient attendance processing tools