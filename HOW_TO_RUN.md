# How to Run the Attendance Tools Suite

## Prerequisites

1. Python 3.7 or higher
2. Required Python packages (install using `pip install -r requirements.txt`)

## Installation Steps

1. **Install Python**: Make sure you have Python 3.7 or higher installed on your system.

2. **Install Dependencies**: 
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```
   python comprehensive_app.py
   ```

4. **Access the Application**: 
   Open your web browser and navigate to `http://localhost:5000`

## If You Encounter Issues

If the application doesn't start or you don't see any output:

1. Try running with verbose output:
   ```
   python -u comprehensive_app.py
   ```

2. Check if Flask is properly installed:
   ```
   python -c "import flask; print(flask.__version__)"
   ```

3. Try the simple version:
   ```
   python simple_attendance_app.py
   ```

## Features Implemented

### 1. Attendance Generator
- **Single Mode**: Process one CSV file with multiple sessions
- **Multiple Mode**: Process multiple CSV files
- Configurable session times and requirements
- Excel report generation

### 2. Raw Excel Generator
- Process multiple Excel files at once
- Extract attendance data from "Attendance" sheets
- Generate standardized raw attendance files

### 3. Attendance Matching
- Match multiple master files with raw attendance files
- Intelligent name matching using fuzzy algorithms
- Support for both Excel and CSV output formats

## File Processing Capabilities

All tools now support processing multiple files simultaneously as requested:

- **Attendance Generator**: Can process either a single file with multiple sessions or multiple files
- **Raw Excel Generator**: Process multiple Excel files in one go
- **Attendance Matching**: Match multiple master files with multiple raw files

## Developer Information

- **Developed By**: Satendra Goswami
- **Instagram**: [@satendragoiswamii](https://www.instagram.com/satendragoiswamii)

## Troubleshooting

If you're having trouble running the application:

1. Make sure all dependencies are installed
2. Check that port 5000 is not being used by another application
3. Try running the command prompt as administrator
4. Check your firewall settings