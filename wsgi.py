# This file contains the WSGI configuration required to serve up your
# web application at http://attendancify.pythonanywhere.com/

import sys
import os

# Add your project directory to the sys.path
path = '/home/attendancify/Attendancify'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'

# Import flask app but need to call it "application" for WSGI to work
from comprehensive_app import app as application

# Ensure the secret key is set for production
application.secret_key = 'ba10a39ed5daeec6bb1f9429fec5c72c1ecf873ec8652585dfc401884570e95ad'