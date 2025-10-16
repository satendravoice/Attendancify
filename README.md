# Attendancify – Attendance Tools Suite
Automated, accurate attendance management for modern education

## 🚀 Live Demo
Try it now: https://attendancify.pythonanywhere.com

## Overview
Attendancify is an automated attendance management suite for online education that processes Zoom and Excel logs to quickly generate attendance reports and identify absent students. Users can upload session logs and master student lists to cross-match attendance, customize time thresholds for marking presence, and download comprehensive Excel reports. The app supports precise attendance tracking and batch processing with easy-to-use tools, and contributions are welcome from the community.

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

5. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage
### Attendance Generation Tool
1. Upload your Zoom session log (Excel format)
2. Set the required time threshold (in seconds)
3. Click "Process" to generate the attendance report
4. Download the processed file with detailed attendance records

### Absentee Report Tool
1. Upload your session attendance file
2. Upload your master student list
3. Click "Generate Report"
4. Download the absentee report showing students who missed the session

### Master Sheet Matching
- Cross-references session attendance with enrollment list
- Identifies students who didn't attend at all
- Produces a comprehensive absentee report
- Useful for compliance and follow-up communication

### Customizable Thresholds
- Admins can set minimum required session time
- Flexible to accommodate different class lengths
- Ensures fairness and consistency in attendance rules

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
