"""
import mysql.connector
import os

class Config:
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'He@th2505',
        'database': 'smart_helmet_db'
    }

    # Secret key for Flask
    SECRET_KEY = os.urandom(24)

    # Twilio configuration
    TWILIO_ACCOUNT_SID = 'ACac2df7a9613653feaac72a034c70da38'
    TWILIO_AUTH_TOKEN = '[AuthToken]'

# Test database connection
connection = None
try:
    connection = mysql.connector.connect(**Config.config)
    if connection.is_connected():
        print("Successfully connected to the database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection is not None and connection.is_connected():
        connection.close()
"""


import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'He@th2505',  # You can also consider using an environment variable for the password
        'database': 'smart_helmet_db'
    }

    # Secret key for Flask
    SECRET_KEY = os.urandom(24)

    # Email configuration for sending password reset emails
    EMAIL_HOST = 'smtp.gmail.com'  # Use Gmail's SMTP server
    EMAIL_PORT = 587  # Port for TLS
    EMAIL_USERNAME = os.getenv('thakkerheath950@gmail.com')  # Fetch email from environment variable
    EMAIL_PASSWORD = os.getenv('lshr uzwb wcdx isfr')  # Fetch password from environment variable

# Test database connection (Optional, usually handled in application code)
def test_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**Config.config)
        if connection.is_connected():
            print("Successfully connected to the database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

# Uncomment the following line to test the connection when running this script
# test_db_connection()
